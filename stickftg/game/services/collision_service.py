class CollisionService:
    def overlap(self, box_a, box_b) -> bool:
        return box_a.rect().colliderect(box_b.rect())
