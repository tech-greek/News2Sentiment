from transformers import pipeline


pipe = pipeline("text-classification", model="ProsusAI/finbert")



if __name__ == "__main__":
    result = pipe("Why TD Cowen Stays Bullish on Apple (AAPL) Stock at $275 PT")
    print(result)
