import flet as ft
import random
import time

def create_animated_background(page: ft.Page):
    # Base deep night layer
    base_layer = ft.Container(expand=True, bgcolor="#06060c")

    # 1. Nebulae Glows (floating ambient light)
    glow1 = ft.Container(
        width=800, height=800, left=-300, top=-300, border_radius=800,
        gradient=ft.RadialGradient(colors=["#14082e", "#06060c"]),
        animate_position=ft.Animation(8000, ft.AnimationCurve.EASE_IN_OUT)
    )
    glow2 = ft.Container(
        width=900, height=900, right=-350, bottom=-200, border_radius=900,
        gradient=ft.RadialGradient(colors=["#062329", "#06060c"]),
        animate_position=ft.Animation(10000, ft.AnimationCurve.EASE_IN_OUT)
    )
    
    # 2. Moving Star Particle System
    star_layer = ft.Stack(expand=True)
    stars = []
    
    # Generate 150 stars that individually float upward
    for _ in range(150):
        size = random.choice([1, 1, 2, 2, 3])
        color = random.choices(["white", "#e2e8f0", "#93c5fd", "#fde047"], weights=[70, 15, 10, 5])[0]
        
        # Each star travels at its own unique speed (between 15 and 40 seconds to cross the screen)
        duration = random.randint(15000, 40000)
        start_top = random.randint(0, 1200)
        
        star = ft.Container(
            width=size, height=size,
            bgcolor=color,
            border_radius=size,
            left=random.randint(0, 2500),
            top=start_top,
            opacity=random.uniform(0.2, 0.9),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=3, color=color) if size > 1 else None,
        )
        star.data = {"duration": duration, "end_time": 0}
        stars.append(star)
        star_layer.controls.append(star)

    bg_stack = ft.Stack(
        expand=True,
        controls=[base_layer, glow1, glow2, star_layer]
    )

    def engine():
        # Give Flet a moment to mount the UI
        time.sleep(1)
        
        # Step 1: Initial launch from their random starting positions
        for s in stars:
            dist_to_travel = s.top + 50
            initial_duration = int((dist_to_travel / 1550.0) * s.data["duration"])
            s.animate_position = ft.Animation(initial_duration, ft.AnimationCurve.LINEAR)
            s.top = -50
            s.data["end_time"] = time.time() + (initial_duration / 1000.0)
            
        try:
            bg_stack.update()
        except:
            pass
            
        last_glow = 0
        
        # Step 2: Continuous Particle Recycling Loop
        while True:
            # Pause animation on opaque routes to save CPU
            if page.route not in ["/", "/login", "/signup", "/forgot-password"]:
                time.sleep(1.0)
                continue

            now = time.time()
            
            # Animate Nebulae every 5 seconds
            if now - last_glow > 5:
                glow1.left = -300 + random.uniform(-100, 100)
                glow1.top = -300 + random.uniform(-100, 100)
                glow2.right = -350 + random.uniform(-100, 100)
                glow2.bottom = -200 + random.uniform(-100, 100)
                last_glow = now
                
            # Find stars that have reached the top (-50)
            to_reset = [s for s in stars if now > s.data["end_time"]]
            
            if to_reset:
                # Silently teleport them back to the bottom of the screen
                for s in to_reset:
                    s.animate_position = ft.Animation(0, ft.AnimationCurve.LINEAR)
                    s.top = 1500
                    s.left = random.randint(0, 2500)
                    
                try:
                    bg_stack.update()
                except Exception as e:
                    if "Event loop is closed" in str(e): return
                    
                # Wait 100ms for Flet to render the teleport
                time.sleep(0.1)
                
                # Re-engage animations and send them upward again
                for s in to_reset:
                    s.animate_position = ft.Animation(s.data["duration"], ft.AnimationCurve.LINEAR)
                    s.top = -50
                    s.data["end_time"] = time.time() + (s.data["duration"] / 1000.0)
                    
            try:
                bg_stack.update()
            except Exception as e:
                if "Event loop is closed" in str(e): return
                
            # Check every 500ms. Extremely light on CPU.
            time.sleep(0.5)

    # engine()  # Removed to prevent blocking the main thread since threading was removed
    return bg_stack
