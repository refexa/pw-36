# -*- coding: utf-8 -*-
import logging
import os

from game import settings
from game.resourcespygame import (
    ImageLoader as _ImageLoader,
    SoundLoader as _SoundLoader,
    FakeImageLoader as _FakeImageLoader,
    MusicLoader as _MusicLoader,
    AnimationResourceLoader as _AnimationResourceLoader,
    FileListResourceLoader as _FileListResourceLoader,
    DirectoryResourceLoader as _DirectoryResourceLoader,
    FakeImageDescription,
    ImageResourceDescription,
    SoundResourceDescription,
    MusicResourceDescription,
    AnimationResourceDescription,
    FileListResourceDescription,
    DirectoryResourceDescription)
from game.settings import Mixer

logger = logging.getLogger(__name__)
logger.debug("importing...")

IRD = ImageResourceDescription
FID = FakeImageDescription
SRD = SoundResourceDescription
MRD = MusicResourceDescription

_res_id = 1000


def next_id():
    global _res_id
    _res_id += 1
    return _res_id


res_id_ship = next_id()
res_id_powerup = next_id()
res_id_mine = next_id()
res_id_enemy_easy = next_id()
res_id_enemy_medium = next_id()
res_id_enemy_hard = next_id()
res_id_cannon = next_id()
res_id_enemy_bullet = next_id()
res_id_enemy_medium_bullet = next_id()
res_id_enemy_hard_bullet = next_id()
res_id_friend_bullet = next_id()
res_id_portal_start = next_id()
res_id_portal_end = next_id()
res_id_pointer = next_id()
res_id_ship_explode = next_id()
res_id_bullet_ship_explosion = next_id()
res_id_bullet_enemy_explosion = next_id()
res_id_ship_wall_sparks = next_id()
res_id_bullet_wall_hit = next_id()

res_id_music_1 = next_id()
res_id_music_2 = next_id()

res_id_sound_fire_1 = next_id()
res_id_sound_fire_2 = next_id()
res_id_sound_fire_3 = next_id()
res_id_sound_fire_4 = next_id()
res_id_sound_fire_5 = next_id()
res_id_sound_fire_6 = next_id()
res_id_sound_game_over = next_id()
res_id_sound_hit = next_id()
res_id_sound_no_bullet = next_id()
res_id_sound_misc_lasers = next_id()  # do not use; this is a composite sample of alternative sounds
res_id_sound_start_level = next_id()
res_id_sound_ship_explode = next_id()  # 3 sec max
res_id_sound_enemy_explode = next_id()  # 3 sec max

hit_animation = AnimationResourceDescription(10, "resources/graphics/hit.png", (0, 0, 57, 57), 1, 3, (0, 1, 2))
resource_config_image = {
    #res_id_ship: ImageResourceDescription("resources/graphics/Rocket (2).gif"),  # FID((32, 32), "white"),
    res_id_ship:AnimationResourceDescription(6, "resources/graphics/fship.png", (0, 0, 42, 42), 1, 5, (0, 1, 2, 3, 4)),
    res_id_powerup: AnimationResourceDescription(10, "resources/graphics/items_health.png", (0, 0, 48, 48), 1, 23,
                                                 (6, 6, 6, 6, 6, 6, 6, 6, 8, 8)),
    res_id_mine: AnimationResourceDescription(10, "resources/graphics/items_health.png", (0, 0, 48, 48), 1, 23,
                                                 (7, 7, 7, 7, 7, 7, 7, 7, 8, 8)),
    res_id_enemy_easy: ImageResourceDescription("resources/graphics/Eship1.png"),  # FID((32, 32), "orange"),
    res_id_enemy_medium: ImageResourceDescription("resources/graphics/Eship2.png"),#FID((32, 32), "orange3")
    res_id_enemy_hard: ImageResourceDescription("resources/graphics/Eship3.png"), #FID((32, 32), "orangered")
    res_id_enemy_bullet: ImageResourceDescription("resources/graphics/Ebullet.png"),  # FID((10, 10), "green"),
    res_id_enemy_medium_bullet: ImageResourceDescription("resources/graphics/ebullet3.png"),#FID((20, 20), "green")
    res_id_enemy_hard_bullet:ImageResourceDescription("resources/graphics/ebullet2.png"),#FID((10, 10), "green")
    res_id_friend_bullet: ImageResourceDescription("resources/graphics/Fbullet.png"),
    res_id_cannon: FID((30, 10), "steelblue1"),
    res_id_portal_end: AnimationResourceDescription(6, "resources/graphics/exitportal.png", (0, 0, 91, 91), 2, 2, [0, 1, 2, 3]),
    res_id_portal_start: AnimationResourceDescription(6, "resources/graphics/entryportal.png", (0, 0, 91, 91), 2, 2, [0, 1, 2, 3]),
    res_id_pointer: ImageResourceDescription("resources/graphics/Crosshair.png"), #FakeImageDescription((10, 10), "white"),
    # res_id_ship_explode: FID((50, 50), "orange"),
    res_id_ship_explode: AnimationResourceDescription(10, "resources/graphics/big_explosion.png", (0, 0, 90, 90), 1, 10,
                                              (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)),
    res_id_bullet_ship_explosion: hit_animation,  # FID((50, 50), "orange"),
    res_id_bullet_enemy_explosion: AnimationResourceDescription(10, "resources/graphics/medium_explosion.png",
                                                                (0, 0, 58, 58), 1, 10, (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)),
    # FID((50, 50), "orange"),
    res_id_ship_wall_sparks: hit_animation,  # FID((50, 50), "orange"),
    res_id_bullet_wall_hit: hit_animation,  # FID((50, 50), "orange"),
}

resource_config_music = {
    res_id_music_1: MRD("resources/audio/bkb-theme.ogg"),
    res_id_music_2: MRD('resources/audio/gumm-theme.ogg'),
}


file_dir = settings.Mixer.file_dir
p_join = os.path.join

DUMMY_SOUND_DESCR = SRD(p_join(file_dir, "Misc_Lasers/Fire_6.ogg"),
                        channel_id=None, volume=0.7)

resource_config_sound = {
    res_id_sound_fire_1: SRD(p_join(file_dir, "Misc_Lasers/Fire_1.ogg"),
                             channel_id=Mixer.player_shoot, volume=0.7),
    res_id_sound_fire_2: SRD(p_join(file_dir, "Misc_Lasers/Fire_2.ogg"),
                             channel_id=Mixer.easy_enemy_shoot, volume=0.7),
    res_id_sound_fire_3: SRD(p_join(file_dir, "Misc_Lasers/Fire_3.ogg"),
                             channel_id=Mixer.medium_enemy_shoot, volume=0.7),
    res_id_sound_fire_4: SRD(p_join(file_dir, "Misc_Lasers/Fire_4.ogg"),
                             channel_id=Mixer.hard_enemy_shoot, volume=0.7),
    res_id_sound_fire_5: SRD(p_join(file_dir, "Misc_Lasers/Fire_5.ogg"),
                             channel_id=Mixer.player_shoot, volume=0.7),
    res_id_sound_fire_6: SRD(p_join(file_dir, "Misc_Lasers/Fire_6.ogg"),
                             channel_id=Mixer.player_shoot, volume=0.7),
    res_id_sound_game_over: SRD(p_join(file_dir, "Misc_Lasers/Game_Over.ogg"),
                                channel_id=None, volume=0.7),
    res_id_sound_hit: SRD(p_join(file_dir, "Misc_Lasers/Hit_1.ogg"),
                          channel_id=Mixer.easy_enemy_explode, volume=0.7, replace=False),
    res_id_sound_no_bullet: SRD(p_join(file_dir, "Misc_Lasers/Game_Over.ogg"),  # todo use appropriate file
                                channel_id=Mixer.player_shoot, volume=0.7),
    res_id_sound_misc_lasers: SRD(p_join(file_dir, "Misc_Lasers/Misc_Lasers.ogg"),
                                  channel_id=None, volume=0.7),
    res_id_sound_start_level: DUMMY_SOUND_DESCR,
    res_id_sound_ship_explode: SRD(p_join(file_dir, 'explosion5.ogg'),
                                  channel_id=None, volume=0.7),
    res_id_sound_enemy_explode: SRD(p_join(file_dir, 'explosion3.ogg'),
                                   channel_id=None, volume=0.7),
}

loaders = {
    IRD: _ImageLoader(),
    SRD: _SoundLoader(),
    FID: _FakeImageLoader(),
    MRD: _MusicLoader(),
    AnimationResourceDescription: _AnimationResourceLoader(),
    FileListResourceDescription: _FileListResourceLoader(),
    DirectoryResourceDescription: _DirectoryResourceLoader()
}

if __name__ == '__main__':
    from game.resources import ResourceLoader

    res_loader = ResourceLoader(loaders)
    res = res_loader.load(resource_config_image)
    print(res)

logger.debug("imported")
