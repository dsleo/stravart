import streamlit as st
import folium
import time
from streamlit_folium import folium_static

if 'study_running' not in st.session_state:
  st.session_state.study_running = False
if 'current_map_data' not in st.session_state:
  st.session_state.current_map_data = None
if 'current_trial_number' not in st.session_state:
  st.session_state.current_trial_number = 0
if 'map_data' not in st.session_state:
  st.session_state.map_data = None
if 'best_map_data' not in st.session_state:
  st.session_state.best_map_data = None


map_center1, final_contour1 = ((48.9022, 2.2855499999999997), [(48.9042, 2.2753), (48.9049, 2.2747), (48.9057, 2.2771), (48.9063, 2.2764), (48.9071, 2.2761), (48.9091, 2.2748), (48.9092, 2.2769), (48.909, 2.2774), (48.9094, 2.2783), (48.9095, 2.2789), (48.9101, 2.2784), (48.9111, 2.2811), (48.911, 2.2814), (48.9116, 2.2819), (48.9113, 2.2823), (48.9121, 2.2847), (48.9138, 2.2836), (48.9149, 2.2862), (48.9148, 2.2874), (48.9146, 2.2867), (48.9138, 2.2877), (48.9143, 2.289), (48.9155, 2.2906), (48.9152, 2.2899), (48.9133, 2.2931), (48.9129, 2.2938), (48.9111, 2.2957), (48.911, 2.2953), (48.9099, 2.2948), (48.9087, 2.293), (48.9082, 2.2928), (48.9086, 2.2949), (48.9091, 2.2957), (48.9102, 2.2982), (48.9106, 2.2989), (48.9085, 2.2999), (48.9078, 2.2963), (48.9074, 2.2971), (48.9072, 2.2971), (48.9056, 2.294), (48.9035, 2.2897), (48.901, 2.2924), (48.9008, 2.2928), (48.8983, 2.2945), (48.898, 2.2983), (48.8974, 2.2975), (48.8986, 2.2955), (48.8983, 2.2945), (48.8955, 2.297), (48.8891, 2.2906), (48.8865, 2.2858), (48.8856, 2.2847), (48.8829, 2.2875), (48.8819, 2.286), (48.8781, 2.2843), (48.8776, 2.2843), (48.8774, 2.284), (48.8775, 2.2837), (48.8781, 2.2806), (48.8781, 2.2809), (48.8773, 2.2836), (48.8775, 2.2837), (48.8774, 2.284), (48.8776, 2.2843), (48.8781, 2.2844), (48.8808, 2.2855), (48.8811, 2.2843), (48.8828, 2.2824), (48.8835, 2.2819), (48.8838, 2.2818), (48.8872, 2.2789), (48.8877, 2.2784), (48.896, 2.2727), (48.8964, 2.2724), (48.8979, 2.2757), (48.8984, 2.275), (48.8986, 2.2748), (48.8998, 2.2778), (48.8996, 2.278), (48.9021, 2.2753), (48.9024, 2.2748), (48.9042, 2.2753), (48.9033, 2.2762), (48.9, 2.268), (48.898, 2.2636), (48.8971, 2.2643), (48.8954, 2.266), (48.8976, 2.2718), (48.8977, 2.2723), (48.8986, 2.2748), (48.8984, 2.275), (48.898, 2.2755), (48.8964, 2.2724), (48.8927, 2.2722), (48.8929, 2.2722), (48.8934, 2.2733), (48.8924, 2.2742), (48.8933, 2.2763), (48.8935, 2.2761), (48.8936, 2.2763), (48.8944, 2.2767), (48.9011, 2.2868), (48.9009, 2.2862), (48.8923, 2.2935), (48.8906, 2.2919), (48.8895, 2.2931), (48.8866, 2.2958), (48.8865, 2.2952), (48.8868, 2.2963), (48.8874, 2.2979), (48.8885, 2.297), (48.8889, 2.2977), (48.8907, 2.3025), (48.8914, 2.3018), (48.8925, 2.3005), (48.8934, 2.2994), (48.8936, 2.2996), (48.9008, 2.2928), (48.9009, 2.2924), (48.905, 2.288), (48.9084, 2.293), (48.9092, 2.2935), (48.9102, 2.2922), (48.9126, 2.2899), (48.9127, 2.2905), (48.911, 2.2917), (48.9101, 2.2881), (48.9102, 2.2879), (48.9098, 2.2807), (48.9074, 2.283), (48.9042, 2.2753)])
map_center2, final_contour2 = ((48.858900000000006, 2.2855499999999997), [(48.8575, 2.2666), (48.8617, 2.2678), (48.8626, 2.2683), (48.8628, 2.2685), (48.8629, 2.2693), (48.8632, 2.2689), (48.8669, 2.272), (48.8678, 2.2699), (48.8693, 2.2714), (48.8702, 2.2695), (48.8711, 2.2716), (48.8729, 2.2726), (48.8731, 2.2729), (48.8736, 2.2737), (48.8738, 2.2747), (48.8736, 2.2742), (48.8733, 2.2739), (48.8761, 2.2749), (48.8758, 2.2739), (48.8766, 2.2752), (48.8773, 2.2784), (48.8774, 2.2789), (48.8772, 2.2788), (48.877, 2.2805), (48.8769, 2.2807), (48.8766, 2.2815), (48.8767, 2.2823), (48.8763, 2.2823), (48.8768, 2.2834), (48.8775, 2.2837), (48.8774, 2.284), (48.8776, 2.2843), (48.8781, 2.2844), (48.8808, 2.2855), (48.8819, 2.2828), (48.8821, 2.283), (48.8824, 2.2827), (48.882, 2.2835), (48.8827, 2.284), (48.884, 2.2861), (48.8846, 2.2883), (48.8844, 2.2882), (48.8843, 2.2886), (48.8842, 2.2889), (48.8841, 2.2893), (48.8819, 2.2937), (48.8813, 2.2927), (48.8786, 2.2959), (48.8783, 2.2954), (48.8779, 2.2971), (48.8776, 2.2982), (48.8759, 2.3031), (48.8746, 2.3014), (48.8744, 2.3008), (48.8738, 2.3006), (48.8738, 2.3018), (48.8735, 2.3019), (48.873, 2.3029), (48.8719, 2.3014), (48.8705, 2.3007), (48.87, 2.3008), (48.867, 2.3011), (48.8666, 2.3011), (48.8658, 2.3012), (48.8646, 2.3012), (48.8625, 2.3015), (48.8626, 2.3021), (48.8625, 2.3032), (48.8623, 2.3032), (48.8624, 2.3067), (48.8597, 2.3079), (48.8598, 2.3088), (48.858, 2.3093), (48.8575, 2.3099), (48.8535, 2.3094), (48.8529, 2.3085), (48.8495, 2.3037), (48.8493, 2.3037), (48.8481, 2.3021), (48.8421, 2.3031), (48.84, 2.3022), (48.8377, 2.2975), (48.8371, 2.2988), (48.831, 2.2925), (48.8309, 2.2927), (48.8292, 2.2925), (48.8281, 2.2925), (48.8228, 2.2924), (48.822, 2.2937), (48.8198, 2.2931), (48.8187, 2.2918), (48.8183, 2.2922), (48.8177, 2.2911), (48.8166, 2.2925), (48.8142, 2.2883), (48.8143, 2.2881), (48.8159, 2.2865), (48.8158, 2.2852), (48.8175, 2.2837), (48.8177, 2.2837), (48.8196, 2.2829), (48.82, 2.2837), (48.8207, 2.283), (48.8217, 2.2819), (48.8247, 2.2822), (48.8264, 2.2801), (48.827, 2.2793), (48.8282, 2.2815), (48.8303, 2.278), (48.831, 2.2788), (48.8325, 2.2792), (48.833, 2.2779), (48.8334, 2.2769), (48.8337, 2.2765), (48.8363, 2.2781), (48.8368, 2.2784), (48.8371, 2.2771), (48.8384, 2.2782), (48.8458, 2.277), (48.8462, 2.2769), (48.8472, 2.2746), (48.8475, 2.2736), (48.8477, 2.2727), (48.8482, 2.2706), (48.8497, 2.2687), (48.8497, 2.2684), (48.8507, 2.2671), (48.853, 2.2647), (48.8555, 2.266), (48.8558, 2.2646), (48.8566, 2.2662), (48.8568, 2.266), (48.8575, 2.2666), (48.8569, 2.2664), (48.8569, 2.2661), (48.8482, 2.2596), (48.8484, 2.2593), (48.8482, 2.2593), (48.848, 2.2593), (48.8478, 2.259), (48.8475, 2.2583), (48.8476, 2.2573), (48.8474, 2.257), (48.8467, 2.2558), (48.8464, 2.2564), (48.8455, 2.2561), (48.8453, 2.2578), (48.8452, 2.2589), (48.84, 2.2672), (48.8389, 2.2696), (48.8388, 2.27), (48.8395, 2.2715), (48.84, 2.2718), (48.8359, 2.2666), (48.8404, 2.2711), (48.8452, 2.2755), (48.8472, 2.2778), (48.8491, 2.2804), (48.8498, 2.2813), (48.8551, 2.2886), (48.8549, 2.2885), (48.8567, 2.2868), (48.8568, 2.2863), (48.8579, 2.2878), (48.8575, 2.2883), (48.8572, 2.2876), (48.8577, 2.2881), (48.8568, 2.2863), (48.8568, 2.2866), (48.8546, 2.289), (48.8526, 2.2909), (48.8523, 2.2906), (48.8478, 2.3013), (48.8422, 2.3031), (48.8418, 2.3033), (48.8405, 2.3043), (48.8407, 2.3048), (48.8363, 2.31), (48.8359, 2.3099), (48.8361, 2.3101), (48.8364, 2.3104), (48.8467, 2.3208), (48.8455, 2.3188), (48.8467, 2.3165), (48.8493, 2.315), (48.8491, 2.3139), (48.8526, 2.3087), (48.8528, 2.3086), (48.8539, 2.3068), (48.8542, 2.3064), (48.8545, 2.306), (48.8546, 2.3058), (48.8617, 2.3022), (48.8626, 2.302), (48.8625, 2.3015), (48.8648, 2.3013), (48.8651, 2.3004), (48.8673, 2.2996), (48.8728, 2.2958), (48.8741, 2.2935), (48.8746, 2.2941), (48.8753, 2.2935), (48.8771, 2.2922), (48.8791, 2.2909), (48.8793, 2.2908), (48.8792, 2.2883), (48.879, 2.2875), (48.8782, 2.2879), (48.8765, 2.2872), (48.8759, 2.2868), (48.8727, 2.2804), (48.8658, 2.2759), (48.8657, 2.2762), (48.8643, 2.273), (48.864, 2.273), (48.8628, 2.2685), (48.8626, 2.2683), (48.8575, 2.2666)])

def generate_fg(final_contour):
  fg = folium.FeatureGroup(name="kook")
  for index, coord in enumerate(final_contour):
      fg.add_child(
          folium.Marker(
          location=[coord[0], coord[1]],
          popup=str(index),
          icon=folium.Icon(color="blue")
      ))
  polyline_coords = [[coord[0], coord[1]] for coord in final_contour]
  fg.add_child(folium.PolyLine(polyline_coords, color="blue", weight=2.5, opacity=1))
  return fg


st.title("StravArt")
n_trials = st.sidebar.number_input('Number of Trials', min_value=3, max_value=50, value=3)
placeholder = st.empty()

for i in range(5):
    if i%2 ==0:
        map_center = map_center1
        final_contour = final_contour1
    else:
        map_center = map_center2
        final_contour = final_contour2
    m = folium.Map(location=map_center, zoom_start=14)
    fg = generate_fg(final_contour)
    fg.add_to(m)
    print(f'Doing {i} trials')
    print(f"Map Center: {map_center}")
    print(f"Final Contour: {final_contour}")


    map_display_width = 700
    map_display_height = 500

    with placeholder.container():
        st.write(f'map center for i={i}: {map_center}')
        folium_static(m, width=map_display_width, height=map_display_height)
        time.sleep(1)

