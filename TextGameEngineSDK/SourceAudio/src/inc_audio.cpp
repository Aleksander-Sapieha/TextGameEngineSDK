
#include "audio.hpp"

#include <alsa/asoundlib.h>

#include <algorithm>
#include <atomic>
#include <cstdint>
#include <fstream>
#include <memory>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

namespace SourceAudio {

struct WavData {
    uint16_t channels = 0;
    uint32_t sample_rate = 0;
    std::vector<int16_t> samples;
};

static uint16_t read16(const unsigned char* p) {
    return uint16_t(p[0]) |
           (uint16_t(p[1]) << 8);
}

static uint32_t read32(const unsigned char* p) {
    return uint32_t(p[0]) |
           (uint32_t(p[1]) << 8) |
           (uint32_t(p[2]) << 16) |
           (uint32_t(p[3]) << 24);
}

static bool load_wav(
    const std::string& path,
    WavData& wav
) {
    std::ifstream file(path, std::ios::binary);

    if (!file)
        return false;

    std::vector<unsigned char> bytes(
        (std::istreambuf_iterator<char>(file)),
        std::istreambuf_iterator<char>()
    );

    if (bytes.size() < 12)
        return false;

    if (std::string(
        reinterpret_cast<const char*>(bytes.data()), 4
    ) != "RIFF")
        return false;

    if (std::string(
        reinterpret_cast<const char*>(bytes.data() + 8), 4
    ) != "WAVE")
        return false;

    uint16_t format = 0;
    uint16_t bits = 0;
    uint16_t block_align = 0;

    bool found_fmt = false;
    bool found_data = false;

    size_t offset = 12;
    size_t data_offset = 0;
    size_t data_size = 0;

    while (offset + 8 <= bytes.size()) {
        const unsigned char* chunk = bytes.data() + offset;

        uint32_t size = read32(chunk + 4);

        size_t start = offset + 8;

        if (size > bytes.size() - start)
            return false;

        if (std::string(
            reinterpret_cast<const char*>(chunk), 4
        ) == "fmt ") {

            if (size < 16)
                return false;

            const unsigned char* fmt = bytes.data() + start;

            format = read16(fmt);
            wav.channels = read16(fmt + 2);
            wav.sample_rate = read32(fmt + 4);
            block_align = read16(fmt + 12);
            bits = read16(fmt + 14);

            found_fmt = true;
        }

        else if (std::string(
            reinterpret_cast<const char*>(chunk), 4
        ) == "data") {

            data_offset = start;
            data_size = size;
            found_data = true;
        }

        offset = start + size + (size & 1);
    }

    if (!found_fmt || !found_data)
        return false;

    if (format != 1 ||
        bits != 16 ||
        (wav.channels != 1 && wav.channels != 2) ||
        wav.sample_rate == 0 ||
        block_align != wav.channels * 2 ||
        data_size == 0 ||
        data_size % block_align != 0)
        return false;

    size_t sample_count = data_size / 2;

    wav.samples.resize(sample_count);

    const unsigned char* data =
        bytes.data() + data_offset;

    for (size_t i = 0; i < sample_count; ++i) {
        wav.samples[i] = static_cast<int16_t>(
            read16(data + i * 2)
        );
    }

    return true;
}

static void play_samples(
    const WavData& wav,
    const std::atomic<bool>& stopping,
    const std::atomic<float>& volume,
    bool loop
) {
    snd_pcm_t* pcm = nullptr;

    int result = snd_pcm_open(
        &pcm,
        "default",
        SND_PCM_STREAM_PLAYBACK,
        0
    );

    if (result < 0)
        return;

    snd_pcm_hw_params_t* params;
    snd_pcm_hw_params_alloca(&params);

    snd_pcm_hw_params_any(pcm, params);

    snd_pcm_hw_params_set_access(
        pcm,
        params,
        SND_PCM_ACCESS_RW_INTERLEAVED
    );

    snd_pcm_hw_params_set_format(
        pcm,
        params,
        SND_PCM_FORMAT_S16_LE
    );

    snd_pcm_hw_params_set_channels(
        pcm,
        params,
        wav.channels
    );

    unsigned int rate = wav.sample_rate;

    result = snd_pcm_hw_params_set_rate_near(
        pcm,
        params,
        &rate,
        nullptr
    );

    if (result < 0 || rate != wav.sample_rate) {
        snd_pcm_close(pcm);
        return;
    }

    result = snd_pcm_hw_params(pcm, params);

    if (result < 0) {
        snd_pcm_close(pcm);
        return;
    }

    constexpr size_t BUFFER_FRAMES = 4096;

    const size_t channels = wav.channels;

    const size_t total_frames =
        wav.samples.size() / channels;

    std::vector<int16_t> buffer(
        BUFFER_FRAMES * channels
    );

    size_t position = 0;

    while (!stopping) {
        if (position >= total_frames) {
            if (!loop)
                break;

            position = 0;
        }

        size_t frames = std::min(
            BUFFER_FRAMES,
            total_frames - position
        );

        float vol = std::clamp(
            volume.load(),
            0.0f,
            1.0f
        );

        size_t count = frames * channels;

        for (size_t i = 0; i < count; ++i) {
            int32_t sample = wav.samples[
                position * channels + i
            ];

            buffer[i] = static_cast<int16_t>(
                std::clamp(
                    static_cast<int32_t>(sample * vol),
                    -32768,
                    32767
                )
            );
        }

        snd_pcm_uframes_t written = 0;

        while (written < frames && !stopping) {
            snd_pcm_sframes_t result = snd_pcm_writei(
                pcm,
                buffer.data() + written * channels,
                frames - written
            );

            if (result < 0) {
                result = snd_pcm_recover(
                    pcm,
                    static_cast<int>(result),
                    1
                );

                if (result < 0)
                    goto finished;

                continue;
            }

            if (result == 0)
                continue;

            written += static_cast<snd_pcm_uframes_t>(
                result
            );
        }

        position += frames;
    }

finished:

    if (stopping)
        snd_pcm_drop(pcm);
    else
        snd_pcm_drain(pcm);

    snd_pcm_close(pcm);
}

struct Audio::Impl {
    WavData music;

    std::atomic<float> music_volume{1.0f};
    std::atomic<float> sound_volume{1.0f};

    std::atomic<bool> music_stopping{false};

    std::thread music_thread;

    std::mutex music_mutex;
    std::mutex sounds_mutex;

    std::vector<std::thread> sound_threads;

    ~Impl() {
        music_stopping = true;

        if (music_thread.joinable())
            music_thread.join();

        std::lock_guard<std::mutex> lock(sounds_mutex);

        for (auto& thread : sound_threads) {
            if (thread.joinable())
                thread.join();
        }
    }
};

Audio::Audio()
    : impl(std::make_unique<Impl>()) {
}

Audio::~Audio() = default;

bool Audio::loadMusic(const std::string& path) {
    WavData wav;

    if (!load_wav(path, wav))
        return false;

    std::lock_guard<std::mutex> lock(
        impl->music_mutex
    );

    impl->music_stopping = true;

    if (impl->music_thread.joinable())
        impl->music_thread.join();

    impl->music = std::move(wav);

    return true;
}

void Audio::playMusic(bool loop) {
    std::lock_guard<std::mutex> lock(
        impl->music_mutex
    );

    if (impl->music.samples.empty())
        return;

    impl->music_stopping = true;

    if (impl->music_thread.joinable())
        impl->music_thread.join();

    impl->music_stopping = false;

    impl->music_thread = std::thread(
        [this, loop]() {
            play_samples(
                impl->music,
                impl->music_stopping,
                impl->music_volume,
                loop
            );
        }
    );
}

void Audio::stopMusic() {
    std::lock_guard<std::mutex> lock(
        impl->music_mutex
    );

    impl->music_stopping = true;

    if (impl->music_thread.joinable())
        impl->music_thread.join();
}

void Audio::setMusicVolume(float volume) {
    impl->music_volume = std::clamp(
        volume, 0.0f, 1.0f
    );
}

void Audio::setSoundVolume(float volume) {
    impl->sound_volume = std::clamp(
        volume, 0.0f, 1.0f
    );
}

bool Audio::playSound(const std::string& path) {
    WavData wav;

    if (!load_wav(path, wav))
        return false;

    std::lock_guard<std::mutex> lock(
        impl->sounds_mutex
    );

    impl->sound_threads.emplace_back(
        [this, wav = std::move(wav)]() {
            std::atomic<bool> stopping{false};

            play_samples(
                wav,
                stopping,
                impl->sound_volume,
                false
            );
        }
    );

    return true;
}

}
