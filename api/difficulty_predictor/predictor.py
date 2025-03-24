
try:
    import pickle
    with open('./api/difficulty_predictor/difficulty_predictor_667.sav', 'rb') as f:
        difficulty = pickle.load(f)
except:
    print("Error during loading difficulty_predictor_667.sav")
    difficulty = None
    pass

# Predict some model
	
def predict(avg_first_passed_total_attempts,avg_first_passed_time_used):
    if not difficulty:
        return 0
    return 0 # int(difficulty.predict([[avg_first_passed_total_attempts,avg_first_passed_time_used]])[0])