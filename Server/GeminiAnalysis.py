import google.generativeai as genai

class GeminiAnalysis:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)  # ✅ configure the API

    def generate(self, index, start_date, end_date):
        prompt = f"Give a brief analysis for {index} between {start_date} and {end_date}. Provide insights about the region's environmental conditions, trends, and potential actions and add the correct unit for each index. If the time period is short, do not mention historical data."
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')  # ✅ Create model
            response = model.generate_content(prompt)         # ✅ Call generate_content on model
            return response.text
        except Exception as e:
            print(f"[Gemini Error] {e}")
            return "Could not generate analysis at this time."
