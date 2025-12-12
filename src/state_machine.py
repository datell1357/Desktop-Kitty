import random

class StateMachine:
    """Simple Finite State Machine for Pet behavior."""
    
    def __init__(self, owner):
        self.owner = owner
        self.state_timer = 0
        self.frame_index = 0
        self.locked = False
        self.current_state = None # Helper for first set_state call
        self.target_duration = 0
        
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
            
            # Override duration for specific states
            if new_state == "sleep":
                self.target_duration = random.randint(5000, 15000)
            elif new_state == "feed":
                self.target_duration = 5000 # 5.0 seconds fixed (0-1-0-1-0)
            elif new_state == "toilet":
                self.target_duration = 4500 # 4.5 seconds fixed
            elif force and new_state == "sit":
                self.target_duration = random.randint(5000, 10000)

    def update(self, dt_ms):
        """Updates state timers and logic."""
        self.state_timer += dt_ms
        
        # Logic for auto-transitions
        if not self.locked:
            self.decide_next_state()

    def step_animation(self):
        """Increments the animation frame index."""
        # Special case: 'feed' runs at 1 frame per second
        if self.current_state == "feed":
            # 0, 1, 0, 1, 0 -> Indices 0, 1, 2, 3, 4
            # Clamp to 4 so it ends on 0.png (5th frame)
            idx = int(self.state_timer / 1000)
            self.frame_index = min(4, idx)
            
        # Special case: 'toilet' runs at 1 frame per second
        elif self.current_state == "toilet":
            # Show frames 0, 1, 2, 3. 
            # We want to ensure it ends on 3.
            # 1 frame per second.
            idx = int(self.state_timer / 1000)
            self.frame_index = min(3, idx) 
            
        else:
            self.frame_index += 1

    def decide_next_state(self):
        """Randomly decides to switch states based on timer."""
        
        # Check Wait Mode
        if self.owner.config.get("wait_mode"):
            return

        # Special case: Sleep lasts longer or user defined
        if self.current_state == "sleep":
            if self.state_timer > self.target_duration: 
                if random.random() < 0.05: 
                    self.set_state("idle")
            return

        # Regular state transitions
        if self.state_timer > self.target_duration:
            if self.current_state == "walk":
                self.set_state("idle")
            elif self.current_state == "idle":
                # Random choice
                states = ["walk", "sit", "idle", "sleep", "jump"]
                weights = [4.0, 1.0, 1.0, 1.0, 0.5]
                choice = random.choices(states, weights=weights, k=1)[0]
                self.set_state(choice)
                
                if choice == "walk":
                    mult = random.uniform(1.0, 4.0)
                    self.target_duration = int(self.target_duration * mult)
                elif choice == "sleep":
                    self.target_duration = random.randint(5000, 15000)

            elif self.current_state == "sit":
                self.set_state("idle")
            elif self.current_state == "jump": 
                self.set_state("idle")
            elif self.current_state == "feed":
                 self.set_state("idle")
            elif self.current_state == "toilet":
                 self.set_state("idle")

            # Reset timer
            self.state_timer = 0
