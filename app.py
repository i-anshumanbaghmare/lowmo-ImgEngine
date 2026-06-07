from src.lowmo.app_factory import build_app

if __name__ == "__main__":
    demo = build_app()
    demo.queue().launch()