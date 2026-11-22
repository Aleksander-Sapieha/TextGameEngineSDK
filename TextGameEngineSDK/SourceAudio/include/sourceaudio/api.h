
#pragma once

#ifdef _WIN32
    #define SA_EXPORT __declspec(dllexport)
#else
    #define SA_EXPORT __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef void* SA_Audio;

SA_EXPORT SA_Audio sa_create();
SA_EXPORT void sa_destroy(SA_Audio audio);

SA_EXPORT int sa_load_music(
    SA_Audio audio,
    const char* path
);

SA_EXPORT void sa_play_music(
    SA_Audio audio,
    int loop
);

SA_EXPORT void sa_stop_music(SA_Audio audio);

SA_EXPORT void sa_set_music_volume(
    SA_Audio audio,
    float volume
);

SA_EXPORT void sa_set_sound_volume(
    SA_Audio audio,
    float volume
);

SA_EXPORT int sa_play_sound(
    SA_Audio audio,
    const char* path
);

#ifdef __cplusplus
}
#endif
