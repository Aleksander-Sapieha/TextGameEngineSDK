
#define MINIAUDIO_IMPLEMENTATION
#include "miniaudio.h"

#include "sourceaudio/audio.hpp"

#include <algorithm>
#include <stdexcept>
#include <vector>

namespace SourceAudio {

struct Audio::Impl {
    ma_engine engine;
    ma_sound* music = nullptr;
    std::vector<ma_sound*> effects;

    float musicVolume = 1.0f;
    float soundVolume = 1.0f;

    Impl() {
        ma_result result = ma_engine_init(nullptr, &engine);

        if (result != MA_SUCCESS) {
            throw std::runtime_error(
                "SourceAudio: Failed to initialize audio engine"
            );
        }
    }

    ~Impl() {
        if (music) {
            ma_sound_uninit(music);
            delete music;
        }

        for (auto* sound : effects) {
            ma_sound_uninit(sound);
            delete sound;
        }

        ma_engine_uninit(&engine);
    }

    static float clampVolume(float value) {
        return std::clamp(value, 0.0f, 1.0f);
    }

    void cleanupEffects() {
        auto it = effects.begin();

        while (it != effects.end()) {
            if (!ma_sound_is_playing(*it)) {
                ma_sound_uninit(*it);
                delete *it;
                it = effects.erase(it);
            } else {
                ++it;
            }
        }
    }
};

Audio::Audio() : impl(std::make_unique<Impl>()) {}

Audio::~Audio() = default;

bool Audio::loadMusic(const std::string& path) {
    if (impl->music) {
        ma_sound_uninit(impl->music);
        delete impl->music;
        impl->music = nullptr;
    }

    auto* sound = new ma_sound();

    ma_result result = ma_sound_init_from_file(
        &impl->engine,
        path.c_str(),
        MA_SOUND_FLAG_STREAM,
        nullptr,
        nullptr,
        sound
    );

    if (result != MA_SUCCESS) {
        delete sound;
        return false;
    }

    ma_sound_set_volume(sound, impl->musicVolume);

    impl->music = sound;
    return true;
}

void Audio::playMusic(bool loop) {
    if (!impl->music)
        return;

    ma_sound_set_looping(impl->music, loop);
    ma_sound_start(impl->music);
}

void Audio::stopMusic() {
    if (impl->music)
        ma_sound_stop(impl->music);
}

void Audio::setMusicVolume(float volume) {
    impl->musicVolume = Impl::clampVolume(volume);

    if (impl->music) {
        ma_sound_set_volume(
            impl->music,
            impl->musicVolume
        );
    }
}

void Audio::setSoundVolume(float volume) {
    impl->soundVolume = Impl::clampVolume(volume);
}

bool Audio::playSound(const std::string& path) {
    impl->cleanupEffects();

    auto* sound = new ma_sound();

    ma_result result = ma_sound_init_from_file(
        &impl->engine,
        path.c_str(),
        0,
        nullptr,
        nullptr,
        sound
    );

    if (result != MA_SUCCESS) {
        delete sound;
        return false;
    }

    ma_sound_set_volume(sound, impl->soundVolume);

    result = ma_sound_start(sound);

    if (result != MA_SUCCESS) {
        ma_sound_uninit(sound);
        delete sound;
        return false;
    }

    impl->effects.push_back(sound);
    return true;
}

}
