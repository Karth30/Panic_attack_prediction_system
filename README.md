# Panic_attack_prediction_system

INTRODUCTION:

In this project, we propose the development of a sensor-enabled assistive device aimed at monitoring and managing stress levels in children with ASD. The device will be equipped with heart rate, skin temperature, and electrodermal activity sensors to detect physiological indicators of stress. Using this data, the system will predict potential panic attacks and immediately notify caretakers through real-time alerts, allowing them to respond proactively. To address the safety concerns of wandering—a behavior often observed in children with autism—a GPS module will be integrated into the system, providing live location tracking and alerting caregivers if the child strays from a safe area.

BLOCK DIAGRAM:

![image](https://github.com/user-attachments/assets/1b9ef13e-6c11-4602-812c-8300c4e2489a)

HARDWARE ARCHITECTURE:

The system leverages the ESP8266 NodeMCU microcontroller, which serves as the central hub for data acquisition and transmission. The following sensors are interfaced with the ESP8266:
●	HW-827 – For Heart Rate (BPM) 
●	TinyGSR – For Galvanic Skin Response (GSR) Voltage levels
●	MAX30205 – For body temperature values
●	GY-NEO-6MV2 – For location tracking: Latitude and Longitude

IMPLEMENTATION:

This project successfully demonstrates the design and implementation of a robust, real-time health and safety monitoring system integrating Internet of Things (IoT), cloud storage, machine learning, and user-friendly web visualization. The system is engineered to collect physiological data such as heart rate, skin conductance (GSR), and body temperature through sensors interfaced with the ESP8266 NodeMCU microcontroller. Additionally, geolocation tracking is enabled through the GY-NEO-6MV2 GPS module to constantly monitor the user's position.
	Data collected from the hardware sensors is transmitted wirelessly and seamlessly logged into Google Sheets using APIs, ensuring efficient and persistent cloud-based storage. This creates a real-time pipeline where data becomes immediately available for processing and visualization. The integration with Streamlit, an open-source Python framework, enables a dynamic graphical user interface (GUI) that not only displays the live sensor data but also computes the user’s location status with reference to a predefined Safe Zone using the Haversine formula for distance calculation.
	A key enhancement of this system is its ability to analyze health conditions using a Random Forest machine learning model trained on collected data, with a reported accuracy of 62%. This model helps in detecting abnormal physiological patterns by learning from the variations in heart rate, temperature, and GSR values, contributing to early warnings or alerts. The prediction and location data, allows the system to display real-time safety status, ensuring that the user is not only physically within a secure area but also biologically stable.
	Moreover, the implementation of a secure login system restricts access to the visualization dashboard, ensuring that only authorized personnel can view or interpret the data. The GUI also allows users to configure safe zone boundaries, enhancing adaptability in diverse applications such as elderly care, mental health monitoring, military or field personnel tracking, and remote health surveillance.
	Through careful hardware-software co-design, this project addresses both the reliability and usability of remote health monitoring. It not only showcases the potential of embedded systems and IoT in health tech but also demonstrates how AI/ML models can be effectively used to provide intelligent insights from sensor data.
The implementation successfully meets its objectives by:
1.	Providing reliable sensor data acquisition,
2.	Enabling seamless cloud integration,
3.	Utilizing machine learning for health status prediction,
4.	Implementing geographic safety measures via the Haversine method,
5.	And offering a secure and intuitive interface for real-time data access.


RESULTS:

![image](https://github.com/user-attachments/assets/4bfa0ce4-f8fd-4437-ac48-6003215a8dbc)

                               Streamlit login page

![image](https://github.com/user-attachments/assets/7203a84d-dc00-4f9d-a5d5-4b4226ebd3f4)

                        Streamlit real-time dashboard

Machine Learning Integration:
      a.	A Random Forest Classifier was trained on previously labeled physiological data with three stress states: Normal, Low Stress, and Panic.
      b. 	The model achieved 62% accuracy on test data and was serialized using Joblib and integrated into the Streamlit app.
![image](https://github.com/user-attachments/assets/c4e0d257-0704-4c8b-a0bf-6ff34969ddc0)

                       Machine learning classification report

![image](https://github.com/user-attachments/assets/322dd1b0-229a-479f-a315-0f41cc9fa31a)

                        Sample inputs and predictions

GPS Location Monitoring:
	a. Displays a map with the user’s current location using the collected coordinates.
![image](https://github.com/user-attachments/assets/09c9a700-c9a1-41df-a5d3-6eb40e5c01e7)
	b. Computes the distance from a defined Safe Zone using the Haversine/Geodesic formula.ϕ1,ϕ2: latitudes (in radians) of point 1 and 2,Δϕ=ϕ2−ϕ1: difference in latitude, Δλ=λ2−λ1: difference in longitude, R: Radius of Earth (mean radius = 6,371 km or 6371000 meters) and d: Distance between the two points (in meters or km)
Haverine/Geodesic formula used for distance computation
![image](https://github.com/user-attachments/assets/dc8be524-dfaf-4f45-a936-1a811a111326)
	c. Safe Zone can be set using the sidebar settings, with three inputs: Latitude, Longitude and Safe Zone Radius in meters.
![image](https://github.com/user-attachments/assets/591ef893-3607-471b-9943-2e3ae367c167)
	d. Visually alerts the user in the app if the device goes outside the defined safety radius (e.g., 10 meters).

Historical Data Table: Both sensor data and GPS logs are available in tabular format for analytical and debugging purposes.
![image](https://github.com/user-attachments/assets/67892f90-9c19-43cb-a46f-a6f0ad640f39)

                                Historical sensor data

![image](https://github.com/user-attachments/assets/b7912db5-4dc4-4a3d-a080-32d4605b7a38)

                               Historical GPS data

![image](https://github.com/user-attachments/assets/bbb3bcaa-93d4-4fad-bd1e-a3f08f0a978d)

History of location tracking
●	Trends Visualisation: The trends of different parameters are visualised for understanding the data obtained.
![image](https://github.com/user-attachments/assets/5e337e37-65c2-412a-b36d-7720a5297fa4)

INFERENCE:

The system was tested under different scenarios:
●	Normal Condition: Low GSR values, stable BPM, and moderate temperature. Model correctly labeled the state as “Normal”.
●	Simulated Stress (Physical Activity): Increased GSR and BPM led to detection of “Low Stress” or “Panic” depending on the magnitude.
●	Sensor Noise Handling: Appropriate filtering and smoothing were implemented for HW-827  to reduce false triggers due to motion artifacts.
●	Safe Zone Violation: When the GPS module was moved outside the defined safe radius, the application accurately computed the distance and triggered a red alert with the “Outside Safe Zone” message.
	All results were recorded and verified using the live dashboard. Plots showed accurate trend representation and latency was typically <2 seconds.

CONCLUSION:

In conclusion, the project presents a holistic and scalable model for remote health monitoring and geofencing that can be extended to include additional sensors or enhanced models. It lays the foundation for further research in personalized healthcare, predictive analytics, and IoT-driven safety systems, potentially transforming how health is monitored and managed in real-world scenarios.

REFERENCES:

[1] Krupa, N., Anantharam, K., Sanker, M. et al. “Recognition of emotions in autistic children using physiological signals,” in Health Technol, Mar. 2016.
doi: 10.1007/s12553-016-0129-3
[2] M. S. Mahmud, H. Fang and H. Wang, "An Integrated Wearable Sensor for Unobtrusive Continuous Measurement of Autonomic Nervous System," in IEEE Internet of Things Journal, vol. 6, no. 1, pp. 1104-1113, Feb. 2019, doi: 10.1109/JIOT.2018.2868235.
[3] R. R. Fletcher et al., "iCalm: Wearable Sensor and Network Architecture for Wirelessly Communicating and Logging Autonomic Activity," in IEEE Transactions on Information Technology in Biomedicine, vol. 14, no. 2, pp. 215-223, March 2010, doi: 10.1109/TITB.2009.2038692.
[4] M. T. Tomczak et al., "Stress Monitoring System for Individuals With Autism Spectrum Disorders," in IEEE Access, vol. 8, pp. 228236-228244, 2020, doi: 10.1109/ACCESS.2020.3045633.
[5] Poh MZ, Swenson NC, Picard RW. A wearable sensor for unobtrusive, long-term assessment of electrodermal activity. IEEE Trans Biomed Eng. 2010 May;57(5):1243-52. doi: 10.1109/TBME.2009.2038487.
[6] H. D. Critchley, “Electrodermal responses: what happens in the brain,” Neuroscientist, vol. 8, pp. 132–142, Apr. 2002
[7] N. Sharma and T. Gedeon, „„Objective measures, sensors and computational techniques for stress recognition and classification: A survey,‟ Comput. Methods Programs Biomed., vol. 108, no. 3, pp. 1287–1301, Dec. 2012.






