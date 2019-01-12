import sys
import os

from .utils import get_cmd_options
from video_game.games.utils import save_transcript

def main(game_type, state, create_player):
    args = get_cmd_options(game_type+' game regression')

    player = create_player(state, args.player_type)
    is_save_transcript = args.save_transcript

    total_game_num = 1000
    done_game_num = 0
    total_score = 0
    total_age = 0
    print_progress = lambda: print('\rtotal game num/done game num/total score/total age: {0}/{1}/{2}/{3}'.format(total_game_num, done_game_num, total_score, total_age), end = '', file = sys.stderr, flush = True)
    print_progress()
    while done_game_num < total_game_num:
        state.reset()
        actions = []
        while not state.is_end():
            action = player.get_action(state)
            state.do_action(action)
            state.update()
            actions.append(action)
        total_score += state.get_score()
        total_age += state.get_age()
        if is_save_transcript:
            save_transcript(os.path.join(os.path.dirname(__file__), game_type+str(game_id)+'.trans'), actions)
        done_game_num += 1
        print_progress()
    print(file = sys.stderr)

