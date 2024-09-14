import time
import turtle
import random
import threading
import pandas as pd
from tkinter import simpledialog, Tk, messagebox

# GLOBAL VARIABLES
states_data = pd.read_csv("50_states.csv")
states_list = states_data.state.to_list()
guessed_states = []
score = 0
timer = 300
hint_counter = 0
stop_event = threading.Event()
game_end = False

# Initialize Tkinter
root = Tk()
root.withdraw()

# SCREEN SETUP
screen = turtle.Screen()
image = "blank_states_img.gif"
screen.title("U.S. States Trivia")
screen.setup(width=760, height=600)
screen.addshape(image)
turtle.shape(image)

label = turtle.Turtle()
label.hideturtle()
label.penup()

timer_turtle = turtle.Turtle()
timer_turtle.hideturtle()
timer_turtle.penup()
timer_turtle.goto(300, 270)


def display_state(state_name, color='black'):
    """Displays entered state on the canvas."""
    chosen_state = states_data[states_data.state == state_name]
    xcor = chosen_state.x.values[0]
    ycor = chosen_state.y.values[0]
    label.goto(xcor, ycor)
    label.color(color)
    label.write(state_name, align="center", font=("Courier", 12, "normal"))


def provide_hint():
    """Gives the player a hint to guess a state."""
    unguessed_states = [state for state in states_list if state not in guessed_states]
    if unguessed_states and timer > 0:
        hint_state = random.choice(unguessed_states)
        messagebox.showinfo("Hint", f"Try guessing: {hint_state[:2]}...")
        print(f"Hint: {hint_state}")


def get_user_input(title, prompt):
    """Shows dialog box for user input."""
    global root
    user_input = simpledialog.askstring(title, prompt)
    return user_input


def simulate_keypress():
    """Simulates a keypress event to close the dialog box."""
    global root
    root.event_generate('<Return>', when='tail')


def update_timer():
    """Controlled by threading to update the timer until it reaches 0."""
    global timer
    while timer > 0 and not stop_event.is_set():
        time.sleep(1)
        timer -= 1


def display_timer():
    """Uses turtle to draw time sequence."""
    if not game_end:
        minutes, seconds = divmod(timer, 60)
        timer_turtle.clear()
        timer_turtle.write(f"{minutes:02d}:{seconds:02d}", align="center", font=("Courier", 18, "normal"))
    if timer > 0:
        screen.ontimer(display_timer, 1000)
    else:
        simulate_keypress()


def end_game(timer_thread):
    """Sequence for ending the game and showing results."""
    global game_end
    missing_states = [state for state in states_list if state not in guessed_states]
    unlearned_states = pd.DataFrame(missing_states)
    unlearned_states.to_csv("states_to_learn.csv", index=False)
    for state in missing_states:
        display_state(state, color='red')
    stop_event.set()
    timer_thread.join()
    game_end = True

    if not missing_states:
        get_user_input("Congratulations!",
                       f"Congratulations! You guessed all 50 states correctly.\n\nPress Enter to exit.")
    else:
        get_user_input("Game Over", f"Game Over! You guessed {score}/50 states correctly.\n"
                                    f"\nCheck 'states_to_learn.csv' for the states you missed.\n\nPress Enter to exit.")


def run():
    """Start the game loop and manage game logic."""
    global timer, score, hint_counter
    timer_thread = threading.Thread(target=update_timer)
    timer_thread.start()
    display_timer()

    while len(guessed_states) < 50 and timer > 0:
        answer_state = get_user_input(f"{score}/50 States Correct",
                                      "Guess a state's name (or type 'Hint' for a hint):\n")
        if answer_state is None:
            break
        answer_state = answer_state.title()
        if answer_state == "Hint":
            provide_hint()
            continue
        if answer_state in states_list and answer_state not in guessed_states:
            score += 1
            guessed_states.append(answer_state)
            display_state(answer_state)
        if answer_state not in states_list:
            hint_counter += 1
            if hint_counter % 3 == 0:
                provide_hint()

    end_game(timer_thread)


if __name__ == "__main__":
    run()
