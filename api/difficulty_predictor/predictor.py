import pickle

# Read sav

with open('./api/difficulty_predictor/difficulty_predictor_667.sav', 'rb') as f:
    difficulty = pickle.load(f)

# Predict some model
	
def predict(avg_first_passed_total_attempts,avg_first_passed_time_used):
    return int(difficulty.predict([[avg_first_passed_total_attempts,avg_first_passed_time_used]])[0])