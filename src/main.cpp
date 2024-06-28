#include <QApplication>
#include <QMainWindow>
#include <QVBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QTextEdit>
#include <QDateTime>
#include <QTcpSocket>
#include <QFile>
#include <QTextStream>
#include <algorithm>
#include <vector>
#include <map>
#include <random>
#include <string>

const QString host = "192.168.0.37";
const int port = 8888;

std::map<int, QString> color_map = {{1, "Green"}, {2, "Green"}, {3, "Red"}, {4, "Red"}};
std::map<int, bool> trajectory_map = {{1, true}, {2, false}, {3, true}, {4, false}};
QString clicked_button_label;

void customPrint(const std::vector<int>& sequence, QTextEdit* textWidget) {
    textWidget->setReadOnly(false);
    textWidget->append("left ");
    for (int num : sequence) {
        QString color = color_map[num];
        bool trajectory = trajectory_map[num];
        if (color == "Green") {
            textWidget->setTextColor(Qt::green);
            textWidget->append(QString::number(trajectory) + " ");
        } else {
            textWidget->setTextColor(Qt::red);
            textWidget->append(QString::number(trajectory) + " ");
        }
    }
    textWidget->append(" right\n");
    textWidget->setReadOnly(true);
}

std::vector<int> genSeq(int numBlock) {
    std::vector<int> sequence;
    switch (numBlock) {
        case 1:
            sequence = {1, 3, 1, 3};
            break;
        case 2:
            sequence = {1, 3, 1, 3};
            break;
        case 3: {
            std::vector<int> seq1 = {1, 3, 1, 3, 1, 3, 1, 3};
            std::vector<int> seq2 = {1, 3, 1, 3, 1, 3, 1, 3};
            std::random_shuffle(seq1.begin(), seq1.end());
            std::random_shuffle(seq2.begin(), seq2.end());
            sequence.insert(sequence.end(), seq1.begin(), seq1.end());
            sequence.insert(sequence.end(), seq2.begin(), seq2.end());
            break;
        }
        case 4: {
            std::vector<int> seq1 = {2, 4};
            std::vector<int> seq2 = {1, 3, 1, 2, 3, 4};
            std::vector<int> seq3 = {1, 2, 3, 4, 1, 2, 3, 4};
            std::random_shuffle(seq1.begin(), seq1.end());
            std::random_shuffle(seq2.begin(), seq2.end());
            std::random_shuffle(seq3.begin(), seq3.end());
            sequence.insert(sequence.end(), seq1.begin(), seq1.end());
            sequence.insert(sequence.end(), seq2.begin(), seq2.end());
            sequence.insert(sequence.end(), seq3.begin(), seq3.end());
            break;
        }
        case 5: {
            std::vector<int> seq1 = {1, 3, 1, 3, 1, 3, 1, 3};
            std::vector<int> seq2 = {1, 3, 1, 3, 1, 3, 1, 3};
            std::random_shuffle(seq1.begin(), seq1.end());
            std::random_shuffle(seq2.begin(), seq2.end());
            sequence.insert(sequence.end(), seq1.begin(), seq1.end());
            sequence.insert(sequence.end(), seq2.begin(), seq2.end());
            break;
        }
    }
    std::random_shuffle(sequence.begin(), sequence.end());
    return sequence;
}

void tcpSendReceived(const QString& data, const std::vector<std::vector<QString>>& seqLog, QTextEdit* textWidget) {
    textWidget->setReadOnly(false);
    textWidget->append("Starting actions for " + clicked_button_label + "!\n");
    textWidget->setReadOnly(true);
    
    QTcpSocket socket;
    socket.connectToHost(host, port);
    if (!socket.waitForConnected(5000)) {
        qDebug() << "Connection failed!";
        return;
    }
    socket.write(data.toUtf8());
    socket.waitForBytesWritten();

    QByteArray buffer;
    while (socket.waitForReadyRead(600000)) {
        buffer.append(socket.readAll());
        if (buffer.contains("ff")) {
            QStringList dataSplit = QString(buffer).split(",");
            std::vector<std::vector<QString>> receivedData;
            std::vector<QString> dataStr;
            for (const QString& item : dataSplit) {
                if (item == "finished") {
                    receivedData.push_back(dataStr);
                    dataStr.clear();
                } else {
                    dataStr.push_back(item);
                }
            }
            // processAndSaveData(receivedData, seqLog);
            break;
        }
    }
    socket.close();
    textWidget->setReadOnly(false);
    textWidget->append(clicked_button_label + " finished successfully!\n");
    textWidget->setReadOnly(true);
}

QString getCurrentDate() {
    return QDateTime::currentDateTime().toString("yyyy-MM-dd");
}

QString getCurrentTime() {
    return QDateTime::currentDateTime().toString("HH:mm:ss");
}

void logStartTime(const QString& filename) {
    QFile file(filename);
    if (file.open(QIODevice::Append)) {
        QTextStream stream(&file);
        stream << "Experiment block start time, " << getCurrentTime() << "\n";
        stream << "Trial no.,Operation time,Color,Trajectory,T/F\n";
    }
}

void processAndSaveData(const std::vector<std::vector<QString>>& receivedData, const std::vector<std::vector<QString>>& seqLog) {
    QString dataFilename = "data_" + getCurrentDate() + ".csv";
    QFile file(dataFilename);
    if (!file.exists()) {
        file.open(QIODevice::WriteOnly);
        file.close();
    }
    logStartTime(dataFilename);
    if (file.open(QIODevice::Append)) {
        QTextStream stream(&file);
        for (size_t i = 0; i < receivedData.size(); ++i) {
            float value = receivedData[i][1].toFloat() / 1000;
            stream << receivedData[i][0] << "," << value << "," << seqLog[i][2] << "," << seqLog[i][3] << "," << seqLog[i][4] << "\n";
        }
    }
}

std::pair<QString, std::vector<std::vector<QString>>> seqRadom(int numBlock, float waitTime, QTextEdit* textWidget) {
    std::vector<int> seq = genSeq(numBlock);
    int lenTrial = seq.size();
    int halfTrial = lenTrial / 2;
    std::vector<int> seqUp(seq.begin(), seq.begin() + halfTrial);
    std::vector<int> seqBottom(seq.begin() + halfTrial, seq.end());

    std::reverse(seqUp.begin(), seqUp.end());
    std::reverse(seqBottom.begin(), seqBottom.end());

    customPrint(seqUp, textWidget);
    customPrint(seqBottom, textWidget);

    std::vector<std::vector<QString>> seqLog;
    QString bits;
    for (int num : seq) {
        QString color = color_map[num];
        bool trajectoryTF = trajectory_map[num];
        std::vector<QString> log = {color, trajectoryTF ? "true" : "false"};
        seqLog.push_back(log);
        bits += (color == "Green" ? (trajectoryTF ? 'z' : 'a') : (trajectoryTF ? 'a' : 'z'));
    }
    QString dataSend = QString::number(lenTrial) + "," + bits + "," + QString::number(waitTime);
    return {dataSend, seqLog};
}

void onButtonClick(int numBlock, float waitTime, QTextEdit* textWidget, const QString& buttonLabel, QPushButton* startButton) {
    clicked_button_label = buttonLabel;
    textWidget->setReadOnly(false);
    textWidget->append("\nYou have selected " + clicked_button_label + " to play!\n");
    textWidget->setReadOnly(true);
    auto [dataSend, seqLog] = seqRadom(numBlock, waitTime, textWidget);
    textWidget->setReadOnly(false);
    textWidget->append("Press start when you are ready!\n");
    textWidget->setReadOnly(true);

    QObject::connect(startButton, &QPushButton::clicked, [=]() {
        tcpSendReceived(dataSend, seqLog, textWidget);
    });
}

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    QMainWindow window;
    QWidget *centralWidget = new QWidget(&window);
    QVBoxLayout *layout = new QVBoxLayout(centralWidget);

    QLabel *label = new QLabel("Choose which block you want to run!", centralWidget);
    layout->addWidget(label);

    QTextEdit *textWidget = new QTextEdit(centralWidget);
    textWidget->setReadOnly(true);
    layout->addWidget(textWidget);

    QPushButton *startButton = new QPushButton("", centralWidget);

    std::vector<std::tuple<QString, int, float>> buttonParams = {
        {"Baseline", 1, 5.0},
        {"Practice", 2, 5.0},
        {"Block 1", 3, 5.0},
        {"Block 2", 4, 5.0},
        {"Block 3", 5, 5.0}
    };

    for (const auto& params : buttonParams) {
        QPushButton *button = new QPushButton(std::get<0>(params), centralWidget);
        QObject::connect(button, &QPushButton::clicked, [=]() {
            onButtonClick(std::get<1>(params), std::get<2>(params), textWidget, std::get<0>(params), startButton);
        });
        layout->addWidget(button);
    }

    window.setCentralWidget(centralWidget);
    window.setWindowTitle("Cobot Malfunction Experiment GUI");
    window.show();

    return app.exec();
}

