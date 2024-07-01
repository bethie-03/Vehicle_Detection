import joblib
import numpy as np

# Example input data
ratio = 0.5
number_of_car = 2
number_of_bike = 10
number_of_truck = 3
number_of_bus = 1


# Prepare the input data in the expected format
input_data = np.array([[ratio, number_of_bike,number_of_car, number_of_bus,number_of_truck ]])
# Load the pre-trained model
model = joblib.load(r'C:\Users\Phan Cong Duy\Downloads\polynomial_regression_model.pkl')


predicted_time = model.predict(input_data)

print(f"Predicted traffic light time: {predicted_time[0]}")