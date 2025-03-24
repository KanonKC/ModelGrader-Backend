try:
    import pandas as pd
    pd.options.mode.chained_assignment = None
    success = True
except:
    success = False

def modelgrader_preprocessor(submission_df):

    # if not success:
    #     return [-1,-1]

    # submission_df = submission_df[['account_id', 'problem_id','is_passed','language','date','submission_code','passed_ratio']]

    # # Change submission_code to string
    # submission_df['submission_code'] = submission_df['submission_code'].astype(str)
    
    # # Sort by account_id, problem_id and date
    # submission_df.sort_values(['account_id','problem_id','date'])

    # # Calculate the difference time between the current submission and the previous submission
    # submission_df['date'] = pd.to_datetime(submission_df['date'])
    # submission_df['diff_time'] = submission_df.groupby(['account_id','problem_id'])['date'].diff()
    # submission_df['diff_time'] = submission_df['diff_time'].dt.total_seconds()

    # # Set all diff_time which is NaN to 0
    # submission_df['diff_time'].fillna(0, inplace=True)

    # # Set all diff_time which has more than 3 hours to 3
    # submission_df.loc[submission_df['diff_time'] > 10800, 'diff_time'] = 10801

    # # Loop each row
    # current_problem_id = None
    # current_account_id = None
    # already_passed = False
    # previous_diff_time = -1


    # for index, row in submission_df.iterrows():
    #     if not current_problem_id and not current_account_id:
    #         current_problem_id = row['problem_id']
    #         current_account_id = row['account_id']

    #     if current_problem_id != row['problem_id'] or current_account_id != row['account_id']:
    #         current_problem_id = row['problem_id']
    #         current_account_id = row['account_id']
    #         already_passed = False
    #     elif already_passed:
    #         # row['diff_time'] = 0
    #         submission_df.drop(index, inplace=True)
    #     elif row['is_passed'] == 1:
    #         already_passed = True
    #         if row['diff_time'] > 10800:
    #             row['diff_time'] = previous_diff_time

    # grouped_submission_df = submission_df.groupby(['account_id','problem_id']).agg({'is_passed':'sum','date':'count','diff_time':'sum'}).reset_index()

    # # Rename columns
    # grouped_submission_df.rename(columns={'date':'first_passed_total_attempts','is_passed':'passed_submission','diff_time':'first_passed_time_used'}, inplace=True)

    # grouped_submission_df = grouped_submission_df.groupby(['problem_id']).agg({'passed_submission':'sum','first_passed_total_attempts':'sum','first_passed_time_used':'mean'}).reset_index()

    # # grouped_submission_df['first_pf_ratio'] = grouped_submission_df['passed_submission'] / grouped_submission_df['first_passed_total_attempts']
    # df = grouped_submission_df.drop(['passed_submission'], axis=1)

    # df.rename(columns={'first_passed_total_attempts':'avg_first_passed_total_attempts','first_passed_time_used':'avg_first_passed_time_used'}, inplace=True)

    # # Change problem_id to index
    # df.set_index('problem_id', inplace=True)

    # return [df['avg_first_passed_total_attempts'][0],df['avg_first_passed_time_used'][0]]
    return [0,0]