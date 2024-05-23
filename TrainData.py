import tensorflow as tf
from tensorflow import keras
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# Verileri yükle
data = pd.read_csv("tic_tac_toe_data.csv")

# X ve y'yi ayır
X = data.iloc[:, :-2].values  # h1'den h9'a kadar olan sütunlar
y = data["move_pos"].values   # Hamle pozisyonu sütunu

# Verileri normalleştir
X = X / 1.0

# Veriyi eğitim ve test olarak ayır
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

# Modeli oluştur
model = keras.Sequential([
    keras.layers.Dense(128, activation='relu', input_shape=(9,)),
    keras.layers.Dropout(0.2),  # Dropout katmanı ekle
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dropout(0.2),  # Dropout katmanı ekle
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dropout(0.2),  # Dropout katmanı ekle
    keras.layers.Dense(9, activation='softmax')
])

# Modeli derle
model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Early stopping
early_stopping = keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

# Modeli eğit
history = model.fit(X_train, y_train, epochs=100, batch_size=32, validation_data=(X_test, y_test), callbacks=[early_stopping])

# Modeli kaydet
model.save("tic_tac_toe_model_improved.keras")

# Eğitim ve doğrulama doğruluklarını yüzdelik olarak yazdır
train_accuracy = history.history['accuracy'][-1] * 100
val_accuracy = history.history['val_accuracy'][-1] * 100
print(f"Eğitim Doğruluğu: {train_accuracy:.2f}%")
print(f"Doğrulama Doğruluğu: {val_accuracy:.2f}%")

# Eğitim ve doğrulama doğruluklarını yüzdelik olarak çizdir
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Eğitim Doğruluğu')
plt.plot(history.history['val_accuracy'], label='Doğrulama Doğruluğu')
plt.title('Eğitim ve Doğrulama Doğruluğu')
plt.xlabel('Epoch')
plt.ylabel('Doğruluk')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Eğitim Kaybı')
plt.plot(history.history['val_loss'], label='Doğrulama Kaybı')
plt.title('Eğitim ve Doğrulama Kaybı')
plt.xlabel('Epoch')
plt.ylabel('Kayıp')
plt.legend()

plt.show()

# Örnek bir giriş örneği seç
sample_input = X_test[0:1]

# Tahminleri yap
predictions = model.predict(sample_input)

# Tahminlerin her birini yüzde cinsinden ifade et
percent_predictions = [f"{prob * 100:.2f}%" for prob in predictions[0]]

# Yüzdelik tahminlerini yazdır
print("Örnek Tahmin: ", percent_predictions)
