from ultralytics import YOLO


def main():
    model = YOLO("yolo11n.pt")

    model.train(
        data="data/dataset/data.yaml",
        epochs=30,
        imgsz=416,
        batch=-1,
        workers=2,
        patience=8,
        device="cpu",
        project="runs",
        name="vehicle_yolo11n_final",
    )

if __name__ == "__main__":
    main()