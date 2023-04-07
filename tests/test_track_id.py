from dotenv import load_dotenv
import util


if __name__ == "__main__":

    input = input("Enter track ID: \n")
    
    prediction = util.predict_vibe(input)
    print(prediction)

    