def get_cmd_options(title):
    import argparse
    from video_game.players import player

    parser = argparse.ArgumentParser(description=title)
    parser.add_argument('player_type', choices=player.PLAYER_TYPES, help='player type')
    parser.add_argument('--save_transcript', action='store_true', help='save transcript')
    args = parser.parse_args()
    return args

def save_transcript(transcript_path, actions):
    with open(transcript_path, 'w') as f:
        for action in actions:
            line = '{0}\n'.format(action)
            f.write(line)

