def get_percent_by_count_of_referrals(ref_count):
    if ref_count >= 21:
        current_percent = 5
    elif ref_count >= 16:
        current_percent = 4
    elif ref_count >= 11:
        current_percent = 3
    elif ref_count >= 6:
        current_percent = 2
    elif ref_count >= 1:
        current_percent = 1
    else:
        current_percent = 0

    return current_percent
