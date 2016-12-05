import logging
from numpy import polyfit, poly1d
import numpy as np
import warnings

from schedule_models import Day


warnings.simplefilter('ignore', np.RankWarning)


def time_cost(meeting_list, best_time):
    # Uses l2 norm between best_time start_time
    sum = 0
    for meeting in meeting_list:
        sum += abs(meeting.start_time - best_time) ** 2
    return sum ** 0.5


# returns p(x) at for some x where p is defined by a grid of points
# uses numpy library with the idea of lagrange multiplier (I think)
def lagrange_evaluator(x_values, y_values):
    return poly1d(polyfit(x_values, y_values, 2))  # len(x_values)))


def gap_cost_poly(x):
    x_values = [15, 15, 4 * 60]
    y_values = [0, 5, 0]
    return max(0, lagrange_evaluator(x_values, y_values)(x))


def gap_cost(meeting_list, preset):
    sum = 0
    for i in range(0, len(meeting_list) - 1):
        # print("PING {}".format(i))
        first_meet = meeting_list[i]
        second_meet = meeting_list[i + 1]
        first_meet_end = first_meet.start_time + first_meet.duration
        gap_time = second_meet.start_time - first_meet_end
        # logging.warn("GAP {}".format(gap_time))
        if gap_time > 20 and gap_time < 4 * 60:
            sum += gap_cost_poly(gap_time) ** 2
    return sum ** 0.5


# best_time is minutes past midnight
def evaluate_schedule(meeting_list, best_time=12 * 60, preset='TODO'):
    sort_by_start = sorted(meeting_list, key=lambda meet: meet.start_time)

    score = 0

    for name, day in Day.__members__.items():
        meets_per_day = list(filter(lambda meet: day in meet.days, sort_by_start))
        day_score = 0
        day_score += time_cost(meets_per_day, best_time)
        day_score += gap_cost(meets_per_day, preset)
        logging.fatal('{} scores {} with meetings of classes {}.'
                      'best_time -> {}, '
                      'gap_cost -> {}'
                      .format(name,
                              day_score,
                              list(map(lambda meet: meet.course_title,
                                       meets_per_day)),
                              time_cost(meets_per_day, best_time),
                              gap_cost(meets_per_day, preset)))
        score += day_score

    return score


# for x in [0, 5, 10, 15, 30, 60, 110, 120, 210]:
#     print('{} -> {}'.format(x, gap_cost_poly(x) ** 2))

# s = ''
# for x in range(0, 480):
#     s += '{:.1f}\t{:.1f}\n'.format(x, gap_cost_poly(x))
# print(s)
