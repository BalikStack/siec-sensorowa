import random
import math
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox

BATTERY_TIME = 60 # czas zycia baterii

# funkcja, która sprawdza, czy wszystkie targety są monitorowane przez przynajmniej jeden sensor
def areAllTargetsMonitored(targets, activeSensors, sensorCoverage):
    monitoredTargets = set()
    for sensor in activeSensors:
        for target in sensorCoverage[sensor]:
            monitoredTargets.add(target)
    return all(target in monitoredTargets for target in targets)


# funckja obliczająca dystans na mapie miedzy dwoma elementami
def calculateDistance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance

# obliczanie maksymalnego czasu zycia sieci dla losowego harmonogramu
def calculateMaxLifeTime(field):
    lifetime = 0
    targets = field.targets
    sensors = []
    for sensor in field.sensors:
        if sensor.status == 'active':
            sensors.append(sensor)

    # tworzymy pustą listę do przechowywania przebiegu włączania i wyłączania sensorów
    sensorsActivityLog = []

    # Definicja zasięgu poszczególnych sensorów (które targety są przez nie monitorowane)
    sensorCoverage = {}

    for sensor in sensors:
        coverage = []
        for target in targets:
            if calculateDistance((sensor.x, sensor.y), (target.x, target.y)) < sensor.range:
                coverage.append(target)
        sensorCoverage[sensor] = coverage
    
    # Lista dostępnych sensorów (które jeszcze nie zostały wyłączone)
    availableSensors = list(sensors)

    # Pętla symulująca losowe włączanie i wyłączanie sensorów
    while availableSensors:
        activeSensors = [] 
        
        for sensor in availableSensors:
            if random.choice([0,0,1]):
                activeSensors.append(sensor)
            if len(activeSensors) == field.nTargets:
                break

        # Sprawdzamy, czy wszystkie targety są monitorowane
        if areAllTargetsMonitored(targets, activeSensors, sensorCoverage):
            # Zapisujemy stan sensorów do listy
            sensorsActivityLog.append(list(activeSensors))
            # Usuwamy użyte sensory z listy dostępnych sensorów
            for sensor in activeSensors:
                availableSensors.remove(sensor)
        # Jeśli nie uda się monitorować wszystkich targetów, pętla może się zakończyć
        else:
            break
        
    stepsWithCoords = {} # przebieg symulacji

    # Wyświetlamy wynikową listę aktywności sensorów wraz z ich koordynatami
    for step, activeSensors in enumerate(sensorsActivityLog):
        lifetime += BATTERY_TIME
       
    
    for step, activeSensors in enumerate(sensorsActivityLog):
        temp = []
        for sensor in activeSensors:
            temp.append((sensor.x,sensor.y))
        stepsWithCoords[step] = temp

    return lifetime, stepsWithCoords


# obliczanie najlepszego czasu
def simulatedAnnealing(field):
    
    temp = 1000
    iterations = 5000
    coolingRate = 0.9
    bestTime, bestRoute = calculateMaxLifeTime(field)
    
    for _ in range(0,iterations):
        newTime, newRoute = calculateMaxLifeTime(field)
        if newTime > bestTime: 
            bestTime = newTime
            bestRoute = newRoute
        elif random.uniform(0,1) < math.exp((newTime-bestTime)/temp):
            bestTime = newTime
            bestRoute = newRoute
        temp *= coolingRate

    return bestTime, bestRoute

# klasa reprezentująca pojdenyczny sensor
class Sensor:
    def __init__(self, x, y, range, status='active'):
        self.x = x
        self.y = y
        self.range = range
        self.status = status

# klasa reprezentująca pojedynczy taget
class Target:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# klasa reprezentująca pole z sensoramia i targetami
class Field:
    def __init__(self):
        self.nSensors = ""
        self.nTargets = ""
        self.fieldSize = ""
        self.sensorRange = ""
    
    def __init__(self, nSensors, nTargets, fieldSize, sensorRange):
        self.nSensors = int(nSensors)
        self.nTargets = int(nTargets)
        self.fieldSize = float(fieldSize)
        self.sensorRange = float(sensorRange)
        
    # generuje pole z sensorami i targetami (wszystkie te elementy są ustawione w punkcie (0,0))
    def generateField(self):
        self.sensors = [Sensor(0, 0, self.sensorRange) for _ in range(self.nSensors)]
        self.targets = [Target(0, 0) for _ in range(self.nTargets)]

    # rozlokowanie elementów na planszy w losowym położeniu
    def raffleTheElements(self):
        for sensor in self.sensors:
            sensor.x = random.uniform(0, self.fieldSize)
            sensor.y = random.uniform(0, self.fieldSize)

        for target in self.targets:
            target.x = random.uniform(0, self.fieldSize)
            target.y = random.uniform(0, self.fieldSize)
        self.setSensorsDeads()

    # sprawdza czy senory moga monitorować jakikolwiek target, jesli nie umierają
    def setSensorsDeads(self):
        for sensor in self.sensors:
            n = 0 
            for target in self.targets:
                if calculateDistance((sensor.x, sensor.y), (target.x, target.y)) > sensor.range:
                    n += 1 
            if n == len(self.targets):
                sensor.status = 'dead'
    
    # zwraca liczbe aktywnych sensorów
    def numOfLiveSensors(self):
        n = 0
        for sensor in self.sensors:
            if sensor.status == 'active': 
                n+=1
        return n
    
    # wyświetla na ekranie plansze 
    def printField(self):
        fig, ax = plt.subplots()
        ax.set_xlim(0, self.fieldSize)
        ax.set_ylim(0, self.fieldSize)

        # wyświetla sensory 
        for sensor in self.sensors:
            if sensor.status == 'active':
                ax.add_patch(plt.Circle((sensor.x, sensor.y), sensor.range, color='blue', alpha=0.1))
                ax.plot(sensor.x, sensor.y, 'bo')
            elif sensor.status == 'dead':
                ax.plot(sensor.x, sensor.y, 'ko')
                # ax.add_patch(plt.Circle((sensor.x, sensor.y), sensor.range, color='black', alpha=0.1))
    
        # wyświetla targety
        for target in self.targets:
            ax.plot(target.x, target.y, 'rv')

        # Tworzy legende
        sensorPatch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='b', markersize=10, label='Active Sensor')
        deadSensorPatch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='k', markersize=10, label='Dead Sensor')
        targetPatch = plt.Line2D([0], [0], marker='v', color='w', markerfacecolor='r', markersize=10, label='Target')
        ax.legend(handles=[sensorPatch, deadSensorPatch, targetPatch])

        ax.set_title('Mapa z sensorami i targetami')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        plt.grid(True)
        plt.show()
 
# pobierane dane wejsciowe od uzytkownika
class Interface:
    def __init__(self, master):
        self.master = master
        master.title("Dane wejściowe")

        # Etykiety i pola tekstowe
        self.labels = ["Rozmiar pola", "Liczba targetów", "Liczba sensorów", "Zasięg sensora"]
        self.entries = {}

        for idx, label in enumerate(self.labels):
            ttk.Label(master, text=label).grid(row=idx, column=0, padx=10, pady=5, sticky=tk.W)
            entry = ttk.Entry(master)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            self.entries[label] = entry

        # Przycisk "Zatwierdź"
        self.submitButton = ttk.Button(master, text="Zatwierdź", command=self.validateAndGetValues)
        self.submitButton.grid(row=len(self.labels), column=0, columnspan=2, pady=10)

        # Etykiety do wyświetlania wyników
        self.resultLabels = {}
        for idx, label in enumerate(self.labels):
            resultLabel = ttk.Label(master, text="")
            resultLabel.grid(row=idx, column=2, padx=10, pady=5)
            self.resultLabels[label] = resultLabel

        # Zmienna przechowująca wartości formularza
        self.values = {}
        self.valid = False

    def validateAndGetValues(self):
        try:
            self.values["Rozmiar pola"] = float(self.entries["Rozmiar pola"].get())
            self.values["Liczba targetów"] = int(self.entries["Liczba targetów"].get())
            self.values["Liczba sensorów"] = int(self.entries["Liczba sensorów"].get())
            self.values["Zasięg sensora"] = float(self.entries["Zasięg sensora"].get())

            # self.values #
            self.valid = True
            
            #uruchamienie własciwego pragramu
            runProgram(self.values["Rozmiar pola"],self.values["Liczba targetów"],self.values["Liczba sensorów"],self.values["Zasięg sensora"])

    

        except ValueError as e:
            messagebox.showerror("Błąd", f"Nieprawidłowa wartość: {e}")
            self.valid = False


def showResult(value,coords):
    root = tk.Tk()
    root.title("Maksymalny czas życia")

    # Tworzenie etykiety z podaną wartością
    label = ttk.Label(root, text=f"Maks. czas życia tej sieci sensorowej to: {value} sekund")
    label.config(font=("Baskerville", 16, "bold"))
    label.pack(padx=20, pady=20)

    
    xValues = list()
    yValues = list()
    
    for key, value in coords.items():
        # print(f"{key} + {len(value)}")
        xValues.append(key*60)
        yValues.append(len(value))


    xValues.append((key+1)*60)
    yValues.append(0)

    
    # Tworzenie wykresu
    plt.figure(figsize=(10, 5))
    plt.plot(xValues, yValues, marker='o')

    # Dodanie tytułu i etykiet osi
    plt.title("Liczba aktywnych sensorów w danej sekundzie")
    plt.xlabel("Czas [s]")
    plt.ylabel("Aktywne sensory [szt.]")

    plt.xticks(range(min(xValues), max(xValues) + 1, 60))
    plt.yticks(range(min(yValues), max(yValues) + 1, 1))

    # Dodanie siatki dla lepszej czytelności
    plt.grid(True)

    # Wyświetlenie wykresu
    plt.show()

    # Uruchomienie głównej pętli aplikacji Tkinter
    root.mainloop()

def runProgram(size,nTargets,nSensors,range):
    board = Field(nSensors,nTargets,size,range)
    board.generateField()
    board.raffleTheElements()
    board.printField()
    time, bestRoute = simulatedAnnealing(board)
    showResult(time, bestRoute)
    for key, value in bestRoute.items():
        print(f"Key: {key}, Value: {value}")

def main():
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()


if __name__ == "__main__":
    main()

