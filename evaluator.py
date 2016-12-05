import logging

from schedule_models import Day


def time_cost(meeting_list, best_time):
    # Uses l2 norm between best_time start_time
    sum = 0
    for meeting in meeting_list:
        sum += (meeting.start_time - best_time) ** 2
    return sum ** 0.5


# best_time is minutes past midnight
def evaluate_schedule(meeting_list, best_time=12 * 60, preset='TODO'):
    sort_by_start = sorted(meeting_list, key=lambda meet: meet.start_time)

    score = 0

    for name, day in Day.__members__.items():
        meets_par_day = filter(lambda meet: day in meet.days, sort_by_start)
        day_score = 0
        day_score += time_cost(meets_par_day, best_time)
        logging.fatal('{} scores {} with meetings of classes {}'
                      .format(name,
                              day_score,
                              list(map(lambda meet: meet.course_title,
                                       meets_par_day))))
        score += day_score

    return score
