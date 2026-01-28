import pygame
from ..core.constants import MOVE_SPEED, JUMP_VELOCITY
from ..models.state import FighterState

class InputController:
    def __init__(self, scheme: dict):
        self.scheme = scheme

    def update(self, fighter):
        keys = pygame.key.get_pressed()


        if fighter.state in (FighterState.HITSTUN, FighterState.DEAD, FighterState.BLOCK_STUN):
            # print(f"DEBUG: Input blocked by state {fighter.state}")
            return
        
        pressed = [k for k in self.scheme.values() if isinstance(k, int) and keys[k]]
        # if pressed:
        #    print(f"DEBUG: Processing input for {fighter.name}. Keys pressed: {pressed} State: {fighter.state}")


        # Defense / Block
        # Defense / Block
        block_key = self.scheme.get("block")
        if block_key is not None and keys[block_key]:
            # Can block if idle, move, or already blocking
            if fighter.state in (FighterState.IDLE, FighterState.MOVE, FighterState.BLOCK):
                fighter.set_state(FighterState.BLOCK)
                fighter.vel.x = 0
                return
        else:
            # If we were blocking, go back to idle
            if fighter.state == FighterState.BLOCK:
                fighter.set_state(FighterState.IDLE)

        # Attack priority
        # Standard Attack (Punch)
        if keys[self.scheme["attack"]]:
            self._handle_attack(fighter, "punch")
            return
            


        move = 0
        if keys[self.scheme["left"]]:
            move -= 1
        if keys[self.scheme["right"]]:
            move += 1

        if move != 0:
            fighter.vel.x = move * MOVE_SPEED
            fighter.facing = 1 if move > 0 else -1
            if fighter.on_ground:
                fighter.set_state(FighterState.MOVE)
        else:
            fighter.vel.x = 0
            if fighter.on_ground:
                fighter.set_state(FighterState.IDLE)

        if keys[self.scheme["jump"]] and fighter.on_ground:
            fighter.vel.y = JUMP_VELOCITY
            fighter.set_state(FighterState.JUMP)


    def _handle_attack(self, fighter, type_str):
        # New Attack (from Idle/Move/Block)
        if fighter.state != FighterState.ATTACK and fighter.state != FighterState.BLOCK:
            fighter.combo_count = 0
            # fighter.attack_type = type_str # Removed
            fighter.set_state(FighterState.ATTACK)
            fighter.vel.x = 0
            
        # Combo Chain logic (Transition)
        elif fighter.state == FighterState.ATTACK:
            # No combo for now, single punch only
            return


