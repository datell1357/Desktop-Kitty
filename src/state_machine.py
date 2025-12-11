import random

class StateMachine:
    """Simple Finite State Machine for Pet behavior."""
    
    def __init__(self, owner):
        self.owner = owner
        self.state_timer = 0
        self.frame_index = 0
        self.locked = False
        self.current_state = None # Helper for first set_state call
        
        # Initialize state properly
        self.set_state("idle", force=True)

    def set_state(self, new_state, force=False):
        """Transitions to a new state."""
        if self.locked and not force:
            return
            
        if self.current_state != new_state:
            self.current_state = new_state
            self.frame_index = 0
            self.state_timer = 0
            # Reset random duration for the new state
            self.target_duration = random.randint(1000, 5000) 
            
            # Override duration for user-forced Sit/Sleep
            if force and new_state in ["sit", "sleep"]:
                self.target_duration = random.randint(5000, 10000)

            # Print debug info (optional)
            # print(f"State changed to: {self.current_state}")

    def update(self, dt_ms):
        """Updates state timers and logic."""
        self.state_timer += dt_ms
        
        # Advance animation frame
        # We can decouple animation speed from logic speed if needed, 
        # but for now we increment frame every tick that exceeds animation interval
        
        # Logic for auto-transitions
        if not self.locked:
            self.decide_next_state()

    def step_animation(self):
        """Increments the animation frame index."""
        self.frame_index += 1

    def decide_next_state(self):
        """Randomly decides to switch states based on timer."""
        
        # Check Wait Mode
        if self.owner.config.get("wait_mode"):
            # If in wait mode, stay in current state (usually forced to Sit)
            return

        # Special case: Sleep lasts longer or user defined
        if self.current_state == "sleep":
            if self.state_timer > self.target_duration: # Use target_duration
                if random.random() < 0.05: # Small chance to wake up per tick after duration
                    self.set_state("idle")
            return

        # Regular state transitions
        if self.state_timer > self.target_duration:
            if self.current_state == "walk":
                self.set_state("idle")
            elif self.current_state == "idle":
                # Random choice: Walk, Sit, Sleep, Jump
                # Random choice: Walk (4x), Sit, Idle, Sleep, Jump (0.5x)
                states = ["walk", "sit", "idle", "sleep", "jump"]
                weights = [4.0, 1.0, 1.0, 1.0, 0.5]
                choice = random.choices(states, weights=weights, k=1)[0]
                self.set_state(choice)
                
                # User Request: Walk duration 1x ~ 4x
                if choice == "walk":
                    mult = random.uniform(1.0, 4.0)
                    self.target_duration = int(self.target_duration * mult)
            elif self.current_state == "sit":
                self.set_state("idle")
            elif self.current_state == "jump": # Explicitly handle jump timeout
                self.set_state("idle")
            
            # Reset timer
            self.state_timer = 0
