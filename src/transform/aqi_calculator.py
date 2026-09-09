BREAKPOINTS = {
 "pm25": [(0,30,0,50),(31,60,51,100),(61,90,101,200),(91,120,201,300),(121,250,301,400),(251,1000,401,500)],
 "pm10": [(0,50,0,50),(51,100,51,100),(101,250,101,200),(251,350,201,300),(351,430,301,400),(431,2000,401,500)],
 "no2": [(0,40,0,50),(41,80,51,100),(81,180,101,200),(181,280,201,300),(281,400,301,400),(401,2000,401,500)],
 "so2": [(0,40,0,50),(41,80,51,100),(81,380,101,200),(381,800,201,300),(801,1600,301,400),(1601,3000,401,500)],
 "co": [(0,1,0,50),(1.1,2,51,100),(2.1,10,101,200),(10.1,17,201,300),(17.1,34,301,400),(34.1,100,401,500)],
 "o3": [(0,50,0,50),(51,100,51,100),(101,168,101,200),(169,208,201,300),(209,748,301,400),(749,2000,401,500)]}
CATEGORIES = [(50,"Good"),(100,"Satisfactory"),(200,"Moderate"),(300,"Poor"),(400,"Very Poor"),(500,"Severe")]
COLORS = {"Good":"#00E400","Satisfactory":"#92D050","Moderate":"#FFFF00","Poor":"#FF7E00","Very Poor":"#FF0000","Severe":"#7E0023"}
def calculate_sub_index(pollutant, value):
    if pollutant not in BREAKPOINTS or value is None: return None
    for low, high, ilow, ihigh in BREAKPOINTS[pollutant]:
        if low <= float(value) <= high:
            return min(500, ilow + (ihigh-ilow)*(float(value)-low)/(high-low))
    return 500 if float(value) > BREAKPOINTS[pollutant][-1][1] else None
def get_aqi_category(value):
    for upper, category in CATEGORIES:
        if value <= upper: return category
    return "Severe"
def get_category_color(category): return COLORS.get(category, "#808080")
def compute_daily_aqi(averages):
    indices = {p: calculate_sub_index(p, v) for p,v in averages.items() if v is not None}
    indices = {p:v for p,v in indices.items() if v is not None}
    if not indices: return {"aqi_value":None,"aqi_category":"Unknown","dominant_pollutant":None}
    dominant = max(indices, key=indices.get); value = indices[dominant]
    return {"aqi_value":round(value,2),"aqi_category":get_aqi_category(value),"dominant_pollutant":dominant}
