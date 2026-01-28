from ..models.state import FighterState

class CombatService:
    def __init__(self, collision):
        self.collision = collision

    def resolve(self, attacker, defender):
        hb = attacker.current_hitbox()
        if hb is None:
            return

        if hb is not None:
            defender_hurtbox = defender.hurtbox()
            hit = self.collision.overlap(hb, defender_hurtbox)
            print(f"DEBUG: {attacker.name} AtkFrame={attacker.state_frame} HB={hb.rect()} Def={defender.name} HURT={defender_hurtbox.rect()} Hit={hit}")
            
            if hit:
                # Damage once per attack (using has_hit flag)
                if attacker.has_hit:
                    return

                attacker.has_hit = True
                
                # Check Block
                blocked = False
                if defender.state == FighterState.BLOCK:
                    # Check direction (must be facing attacker)
                    # Defender facing: 1 (right), -1 (left)
                    # Attacker is to the left if attacker.pos.x < defender.pos.x
                    # If attacker is to left, defender must face left (-1) to block.
                    direction_to_attacker = -1 if attacker.pos.x < defender.pos.x else 1
                    if defender.facing == direction_to_attacker:
                        blocked = True

                if blocked:
                    # Chip damage or 0
                    damage = 0
                    defender.hp = max(0, defender.hp - damage)
                    
                    # Pushback (Attacker slides back or Defender slides back?)
                    # Standards: Defender slides back on block.
                    defender.vel.x = attacker.facing * (attacker.attack_def.knockback_x * 0.5)
                    defender.vel.y = 0 # No vertical knockback on block usually
                    
                    defender.hitstun_left = attacker.attack_def.recovery # Block stun roughly equal to recovery?
                    # Or a fixed block stun.
                    defender.set_state(FighterState.BLOCK_STUN)
                    print(f"DEBUG: BLOCKED! {defender.name} HP={defender.hp}")
                else:
                    # Hit
                    defender.hp = max(0, defender.hp - attacker.attack_def.damage)

                    defender.vel.x = attacker.facing * attacker.attack_def.knockback_x
                    defender.vel.y = -240.0

                    defender.hitstun_left = 16
                    defender.set_state(FighterState.HITSTUN)
                    print(f"DEBUG: HIT! {defender.name} HP={defender.hp}")
