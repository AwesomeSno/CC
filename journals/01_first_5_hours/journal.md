# MEMENTO - Devlog

**5h**

## First 5 Hours: Problem Definition, Architecture & Hardware Foundations

I've been thinking a lot about how most note-taking apps and audio recorders work. You record a voice memo on your phone or use some smart recorder, and it just dumps a giant multi-gigabyte audio file into a folder that you never open again. Or if it does transcribe it, it sends all your private conversations to someone's cloud servers and gives you a robotic block of text that completely strips away the tone, the hesitation, and whether someone actually agreed with what you said.

For Half Life, I wanted to build something I'd actually use every day: MEMENTO. It's a small wearable recorder that clips onto your shirt or sits on your desk, captures conversations locally to a microSD card, and when you plug it into your Mac, it transcribes everything completely offline, figures out who was speaking, and analyzes how the conversation went. Like if you're in an interview, it can tell you if you rambled, if you actually answered what they asked, or if you made commitments you might forget.

In these first 5 hours, I focused on defining the core problem, sketching out the high-level system architecture, selecting the ESP32-S3 microcontroller, mapping out the GPIO pinout budget, designing the acoustic porting for the INMP441 microphone, and working through the battery and power management tree.

Here are the sketches and plans from the first 5 hours.

---

### 01: Why existing recorders fall short

Most voice memos just end up sitting in a dead folder. They don't know who was speaking, they don't extract action items, and cloud options force you to upload private talks to third-party servers. MEMENTO is built around local hardware capture, offline processing on your Mac, and linking every observation straight back to the original audio timestamp.

![01_problem_passive_recorders](images/01_problem_passive_recorders.png)

---

### 02: High-level system architecture

I broke the project down into three main parts: the physical recorder, the transfer bridge, and the desktop intelligence engine. The hardware handles clean I2S audio acquisition and saves it directly to microSD. Once connected to the Mac, local models handle speech-to-text, speaker diarization, acoustic features, and LLM extraction.

![02_memento_system_block_diagram](images/02_memento_system_block_diagram.png)

---

### 03: Picking the MCU and pinout budget

I went with the ESP32-S3-WROOM-1 with 8MB flash and 8MB PSRAM. It has native USB support, hardware I2S DMA for the mic, and fast SPI for the microSD card. I mapped out all the GPIO pins carefully so the high-speed audio lines don't interfere with the buttons, OLED display, or power management.

![03_esp32s3_pinout_budget](images/03_esp32s3_pinout_budget.png)

---

### 04: Microphone acoustic design and noise isolation

If the microphone captures muffled or noisy audio, no AI model in the world can fix it. I picked the INMP441 digital I2S MEMS mic. To make sure voice comes through clearly, I designed a front acoustic funnel with a 1.5mm opening, added a silicone damping ring to isolate it from casing vibrations, and gave it an isolated analog ground plane on the PCB.

![04_inmp441_acoustic_porting](images/04_inmp441_acoustic_porting.png)

---

### 05: Power tree and battery management

For battery life, I chose a 1200mAh 3.7V LiPo cell with built-in protection. The board takes 5V over USB-C, charges through a TP4056 linear charger, and feeds an ultra-low-noise ME6211 3.3V LDO regulator. In recording mode with the OLED dimmed, current draw is around 65mA, which gives easily 14 or more hours of continuous recording.

![05_power_tree_and_battery](images/05_power_tree_and_battery.png)
