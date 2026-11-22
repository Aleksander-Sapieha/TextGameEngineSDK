
#pragma once

#include <memory>
#include <string>

namespace SourceAudio {

class Audio {
public:
    Audio();
    ~Audio();

    Audio(const Audio&) = delete;
    Audio& operator=(const Audio&) = delete;

    bool loadMusic(const std::string& path);
    void playMusic(bool loop = false);
    void stopMusic();

    void setMusicVolume(float volume);
    void setSoundVolume(float volume);

    bool playSound(const std::string& path);

private:
    struct Impl;
    std::unique_ptr<Impl> impl;
};

}
