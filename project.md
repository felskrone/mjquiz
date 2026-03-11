# Goal
I want to create a simple minecraft quiz app that i can host on render.com.

# Requirements
URL: mjquiz.onrender.com
The format of the quiz is always a question with 4 possible answers 1,2,3,4.
Read the quiz questions from a simple text file in the format:

"""
Question1: <text>
Correct Answer: <1-4>


Question2: <text>
Correct Answer: <1-4>
"""

Keep a score for everytime the quiz is taken and write the results into flat text file 'highscores.txt'.
The highscores.txt file shall never contain more than the top 10 entries with the highest scores.
The top 10 scores always be displayed on the starting page of the quiz.


# Technologies
Flask framework