#include "mainwindow.h"
#include "ui_mainwindow.h"



MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    //setVideoName("0");
    //process();

    //createCameraSignalSlots();
    socket = new QUdpSocket(this);
    socket->bind(QHostAddress("127.0.0.1"), 20022);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::appExit()
{
    close();
}


const std::string currentDateTime() {
    time_t     now = time(0);
    struct tm  tstruct;
    char       buf[80];
    tstruct = *localtime(&now);
    // Visit http://en.cppreference.com/w/cpp/chrono/c/strftime
    // for more information about date/time format
    strftime(buf, sizeof(buf), "%Y-%m-%d.%X", &tstruct);

    return buf;
}
void MainWindow::on_pushButton_clicked()
{
    QString filename = QFileDialog::getOpenFileName(this, "Open Video File");

    if(setVideoName(filename))
    {
        process();
    }

    // Added by Dan 06/17/2017
    //dbNumber = ui->dbBox->text().toInt();
   // int dbNumber = 8;
    //int hiveNumber = 1;
    //hiveNumber = ui->hiveBox->text().toInt();

    QString DBset = "DB number set to: " + QString::number(dbNumber);
    QString HiveSet = "Hive number set to: " + QString::number(hiveNumber);

    // trackListWidget->addItem(DBset);
    //trackListWidget->addItem(HiveSet);

    if (CONNECT_STAT == 0)
    {
        temperature = "0";
        humidity = "0";
        //  trackListWidget->addItem("WARNING:NO SENSOR CONNECTED");
    }

}
// Added by DAN 6/13/2016
void MainWindow::on_pushButton_sampleDB_clicked()
{

    //qDebug() << "Send data via UDP";
    QByteArray Data;
    Data.append("");


    //showStatusBarMessage(dbBox->value());
    // Sends the datagram datagram
    // to the host address and at port.
    // qint64 QUdpSocket::writeDatagram(const QByteArray & datagram,
    //                      const QHostAddress & host, quint16 port)



    socket->writeDatagram(Data, QHostAddress("127.0.0.1"), 20022);

}
//////////////////////////////////////////////////////

/////////////////////////////// Added by DAN 6/23/2016
/*void MainWindow::on_connectSensorButton_clicked()
{
    comNumber = ui->serialBox->text().toInt();
    QString comPort = "COM" + QString::number(comNumber);

    if (comNumber <= 0 || comNumber == 1)
    {
        qDebug() << "Failed to connect!";
    }
    else
    {
        //connectSerialPort(comPort);
    }

} */
void MainWindow::on_button_stop_clicked()
{
    stop();
}
// Added by DAN 6/13/2016

//void MainWindow::on_pushButtonExitApp_clicked()
//{
//    stop();
//}

int MainWindow::setVideoName(QString &filename)
{
    if(!filename.isEmpty())
    {
        videofilename = filename;
        return 1;
    }
    return 0;
}

int MainWindow::stop()
{
    running = false;
}
clock_t t;

int n_frame = 0;
int MainWindow::process()
{
    //cv::Size re_size = cv::Size(695, 480);

    cv::Scalar Colors[] = { cv::Scalar(255, 0, 0), cv::Scalar(0, 255, 0), cv::Scalar(0, 0, 255), cv::Scalar(255, 255, 0), cv::Scalar(0, 255, 255), cv::Scalar(255, 0, 255), cv::Scalar(255, 127, 255), cv::Scalar(127, 0, 255), cv::Scalar(127, 0, 127) };

    std::string cfg_file = "data/yolov2-tiny_obj.cfg";
    std::string weights_file = "data/yolov2-tiny_obj_17000.weights";
    std::string names_file = "data/bee.names";
    Detector detector(cfg_file, weights_file);
    auto obj_names = objects_names_from_file(names_file);



    cv::VideoCapture capture(videofilename.toStdString());
   //  VideoCapture capture(1);
    if (!capture.isOpened())
    {
        //error in opening the video input
        cerr << "Unable to open video file: " << endl;
        exit(EXIT_FAILURE);
    }

//    int frame_width=   capture.get(CAP_PROP_FRAME_WIDTH);
//    int frame_height=   capture.get(CAP_PROP_FRAME_HEIGHT);
//    int codec = cv::VideoWriter::fourcc('M', 'J', 'P', 'G');
//    VideoWriter video("demo2-report.avi", codec, 10, Size(frame_width, frame_height), true);
capture.set(cv::CAP_PROP_FRAME_WIDTH, 640); // valueX = your wanted width
capture.set(cv::CAP_PROP_FRAME_HEIGHT, 480); // valueY = your wanted heigth
    cv::Mat frame;




    //CDetector detector(frame);
    CTracker tracker(1.0f, 0.2f, 85.0f, 5, 60);
    running = true;
    //long totalFrameNumber = capture.get(CV_CAP_PROP_FRAME_COUNT);

    //cv::Rect myROI(10,0,620,480);
    while (true)
    {


        bool bSuccess = capture.read(frame); // read a new frame from video

        n_frame ++;

        if (!bSuccess) //if not success, break loop
        {
            cout << "Cannot read a frame from video stream" << endl;
            break;
        }
        //  cv::resize(frame, frame, re_size);
        //frame = frame(myROI);

        //CDetector detector(frame);
        //detector.SetMinObjectSize(cv::Size(frame.cols / 20, frame.rows / 10));

       // t = clock();
       // std::vector<bbox_t> result_vec = detector.detect(mat_to_image(frame));

        std::shared_ptr<image_t> darknet_image = detector.mat_to_image(frame);
            vector<bbox_t> result_vec = detector.detect(*darknet_image);


        draw_boxes(frame, result_vec, obj_names);
        //show_result(result_vec, obj_names);
        //QString obj_name = get_name(result_vec, obj_names);


        //const std::vector<Point_t>& centers = detector.Detect(frame);
        //const std::vector<cv::Rect>& rects = detector.GetDetects();


        //update track
        const std::vector<Point_t>& centers = GetCenters(result_vec,obj_names);
        const std::vector<cv::Rect>& rects = GetRects(result_vec,obj_names);
        tracker.Update(centers, rects, CTracker::RectsDist);
        const std::vector<int>& obj_ids = get_ids(result_vec, obj_names);
        //qDebug() << "The slow operation took" << timer.elapsed() << "milliseconds";
        //std::cout << rects.size()<< std::endl;
        for (auto p : centers)
        {
            cv::circle(frame, p, 3, cv::Scalar(0, 255, 0), 1, CV_AA);


        }
        for (int i=0; i<centers.size(); i++)
        {
            Yolo_array.push_back(Point3f(centers[i].x,centers[i].y,obj_ids[i]));


        }
        //only store the lastest 20 tracked points, this number can be optimize

        if (Yolo_array.size()>20)
        {
            Yolo_array.erase(Yolo_array.begin(),Yolo_array.end()-10);
        }


        //tracker.Update(centers, rects, CTracker::RectsDist);

        //tracking
        //std::cout << "CPU 1: " <<(long double)(std::clock() - start)/CLOCKS_PER_SEC << std::endl;
        // start = std::clock();



       // std::cout << Yolo_array.size() << std::endl;

        //cv::resize(img2, img2,re_size);
#pragma omp parallel for // this can boost the processing time
        for (int i = 0; i < tracker.tracks.size(); i++)
        {
            // cv::rectangle(frame, tracker.tracks[i]->GetLastRect(), cv::Scalar(0, 255, 0), 1, CV_AA); // draw a rectangular box around the object detected by Kalman Filter

            if (tracker.tracks[i]->trace.size() > 1)
            {
#pragma omp parallel for
                for (int j = 0; j < tracker.tracks[i]->trace.size() - 1; j++)
                {
                    cv::line(frame, tracker.tracks[i]->trace[j], tracker.tracks[i]->trace[j + 1], Colors[tracker.tracks[i]->track_id % 9], 2, CV_AA);
                    // }

                    //reverseArr(Yolo_array,Yolo_array.size()-50,Yolo_array.size());

                    for(int k=0; k< Yolo_array.size();k++)
                    {
                        if((abs(tracker.tracks[i]->trace[j].x-Yolo_array[k].x)<1)&&(abs(tracker.tracks[i]->trace[j].y-Yolo_array[k].y)<1))
                            // if((abs(KF_array[i].x-Yolo_array[k].x)<2)&&(abs(KF_array[i].y-Yolo_array[k].y)<2))
                        {
                              KF_array.push_back(Point3f(tracker.tracks[i]->trace[j].x,tracker.tracks[i]->trace[j].y,Yolo_array[k].z));

                             //std::cout<<"size of "<<tracker.tracks[i].size()<<std::endl;
                            //std::cout<<"x: "<<tracker.tracks[i]->trace[j].x<<"y:"<<tracker.tracks[i]->trace[j].y<<"z:"<<Yolo_array[k].z<<std::endl;
                            // int BeeIds = 0;
                            //KF_array[j].z = Yolo_array[k].z;

                            // Some computation here
                            //  int BeeNum = KF_array[j].z;
                            //                            int BeeId1 = Yolo_array[k].z;
                            //                            int BeeId2 = Yolo_array[k-1].z;
                            //                            int BeeId3 = Yolo_array[k-2].z;
                            //                            int BeeId4 = Yolo_array[k-3].z;
                            //                            std::cout<<BeeId1<<","<<BeeId2<<","<<BeeId3<<","<<BeeId4<<std::endl;
                            //                            int BeeId_arr[] = {BeeId1, BeeId2, BeeId3, BeeId4};
                            //int BeeIds = findCandidate(BeeId_arr,4);

                            int BeeIds = Yolo_array[k].z;

                            // std::time_t end_time = std::chrono::system_clock::to_time_t(start);
                            //std::cout<<"result: "<<BeeIds<<"ttime:= "<<std::ctime(&end_time)<<std::endl;
                           // std::cout<<"result: "<<BeeIds<<std::endl;


                            QDateTime fileDateTime = QDateTime::currentDateTime();
                            QString fileTimeStamp = fileDateTime.toString("yyyyMMdd");
                            //  QString rootPath = QString(".");
                            QString fileName = QString("%1.txt").
                                    //    arg(rootPath).
                                    arg(fileTimeStamp);
                            float distance = tracker.tracks[i]->trace[0].y - tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].y;

                            //std::cout<<"IDd"<<BeeIds<<"Dis:="<<distance<<"Y: "<<tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].y<<std::endl;
                            // std::cout<<"Y:="<<tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].y<<std::endl;
                            //  putText(frame, std::to_string(round(tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].y)), Point2f(tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].x+10,tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].y), cv::FONT_HERSHEY_COMPLEX_SMALL, 0.5, Colors[3]);

                            // putText(frame, std::to_string(BeeId1), Point2f(tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].x+10,tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].y), cv::FONT_HERSHEY_COMPLEX_SMALL, 0.8, Colors[3]);

//                            t = clock() - t;
//                            int fps = round(((float)n_frame) / (((float)t)/CLOCKS_PER_SEC ));

//                            if (fps <50)
//                            {
//                                putText(frame,"FPS: "+std::to_string(fps), cv::Point2f(200, 45), cv::FONT_HERSHEY_COMPLEX_SMALL, 0.8, Colors[4]);

//                            }
                            //putText.clear();



                            if((abs(distance) >MOVE_DISTANCE)&&(abs(tracker.tracks[i]->trace[0].y)>abs(tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].y))&&(abs(tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].y<50))&&(BeeIds==0))
                            {

                                if((!tracker.tracks[i]->is_in)&&(!tracker.tracks[i]->is_bee))
                                {

                                    tracker.tracks[i]->is_in =true;
                                    tracker.tracks[i]->is_bee = true;

                                    std::cout<<currentDateTime()<<" BEE IS IN"<<std::endl;
                                    putText(frame, "BEE IN", cv::Point2f(50, 45), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.0, Colors[1]);
                                    // Yolo_array.clear();
                                    QDateTime dateTime = QDateTime::currentDateTime();
                                    QString timeStamp = dateTime.toString("yyyy-MM-dd.hh:mm:ss");
                                    //ui->trackListWidget->addItem(timeStamp);
                                    //ui->trackListWidget->addItem("IS IN");
                                    ////////////////////////////////////////////////////////////
                                    // Added by Dan 06/13/2016
                                    // Updated 06/23/2016 - added temp+hum

                                    // format: HIVE#:BEE_TAG:ACTION:VALUE:DB_ID
                                    QByteArray Data;

                                    // Added by Dan 06/17/2017
                                    dbNumber = ui->dbBox->text().toInt();
                                    hiveNumber = ui->hiveBox->text().toInt();

                                    // HIVE#
                                    //     Data.append(QString::number(hiveNumber) + ":" + timeStamp + ":IN:" + temperature + ":" + humidity + ":" + QString::number(dbNumber) + ":");

                                    Data.append("B:ACT:IN:" + timeStamp + ":"+QString::number(0) );

                                    socket->writeDatagram(Data, QHostAddress("127.0.0.1"), 20022);
                                    //QString tagImgFn("20160718/"+ "_OUT" + ".jpg"); // increase with number
                                    //cv::imwrite(tagImgFn.toStdString(), image);
                                    QFile file(fileName);

                                    if (file.open(QIODevice::Text | QIODevice::Append)) {
                                        QTextStream fileStream(&file);
                                        fileStream << timeStamp+ " ";
                                        fileStream << "PM BEE IS IN" << endl;
                                    }

                                    file.close();

                                }//end if
                            }//end if

                            //std::cout<<"Y:="<<tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].y<<std::endl;

                            if((abs(distance)>MOVE_DISTANCE)&&(abs(tracker.tracks[i]->trace[0].y)<abs(tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].y))&&(abs(tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].y)>400)&&(BeeIds==0))
                            {
                                if((!tracker.tracks[i]->is_out)&&(!tracker.tracks[i]->is_bee))
                                {

                                    //                      outF <<currentDateTime()<<" IS OUT"<<std::endl;


                                    tracker.tracks[i]->is_out=true;
                                    tracker.tracks[i]->is_bee = true;
                                    std::cout<<currentDateTime()<<"BEE IS OUT"<<std::endl;
                                    putText(frame, "BEE OUT", cv::Point2f(500, 390), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.0, Colors[1]);
                                    // Yolo_array.clear();

                                    QDateTime dateTime = QDateTime::currentDateTime();
                                    QString timeStamp = dateTime.toString("yyyy-MM-dd.hh:mm:ss");
                                    //ui->trackListWidget->addItem(timeStamp);
                                    //ui->trackListWidget->addItem("IS OUT");
                                    ////////////////////////////////////////////////////////////
                                    // Added by Dan 06/13/2016
                                    // Updated 06/23/2016 - added temp+hum

                                    // format: HIVE#:BEE_TAG:ACTION:VALUE:DB_ID
                                    QByteArray Data;

                                    // Added by Dan 06/17/2017
                                    dbNumber = ui->dbBox->text().toInt();
                                    hiveNumber = ui->hiveBox->text().toInt();

                                    // HIVE#
                                    //     Data.append(QString::number(hiveNumber) + ":" + timeStamp + ":IN:" + temperature + ":" + humidity + ":" + QString::number(dbNumber) + ":");
                                    Data.append("B:ACT:OUT:" + timeStamp + ":"+QString::number(0));

                                    socket->writeDatagram(Data, QHostAddress("127.0.0.1"), 20022);
                                    //QString tagImgFn("20160718/"+ "_OUT" + ".jpg"); // increase with number
                                    //cv::imwrite(tagImgFn.toStdString(), image);
                                    QFile file(fileName);

                                    if (file.open(QIODevice::Text | QIODevice::Append)) {
                                        QTextStream fileStream(&file);
                                        fileStream << timeStamp+ " ";
                                        fileStream << "PM BEE IS OUT" << endl;
                                    }

                                    file.close();
                                } //end if

                            }//end if




                            if((abs(distance) >MOVE_DISTANCE)&&(abs(tracker.tracks[i]->trace[0].y)>abs(tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].y))&&(abs(tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].y<50))&&(BeeIds==1))
                            {

                                if((!tracker.tracks[i]->is_in)&&(!tracker.tracks[i]->is_pollen))
                                {

                                    tracker.tracks[i]->is_in =true;
                                    tracker.tracks[i]->is_pollen = true;

                                    std::cout<<currentDateTime()<<" POLLEN IS IN"<<std::endl;
                                    putText(frame, "POLLEN IN", cv::Point2f(50, 45), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.0, Colors[1]);
                                    // Yolo_array.clear();
                                    QDateTime dateTime = QDateTime::currentDateTime();
                                    QString timeStamp = dateTime.toString("yyyy-MM-dd.hh:mm:ss");
                                    //ui->trackListWidget->addItem(timeStamp);
                                    //ui->trackListWidget->addItem("IS IN");
                                    ////////////////////////////////////////////////////////////
                                    // Added by Dan 06/13/2016
                                    // Updated 06/23/2016 - added temp+hum

                                    // format: HIVE#:BEE_TAG:ACTION:VALUE:DB_ID
                                    QByteArray Data;

                                    // Added by Dan 06/17/2017
                                    dbNumber = ui->dbBox->text().toInt();
                                    hiveNumber = ui->hiveBox->text().toInt();

                                    // HIVE#
                                    //     Data.append(QString::number(hiveNumber) + ":" + timeStamp + ":IN:" + temperature + ":" + humidity + ":" + QString::number(dbNumber) + ":");

                                    Data.append("B:ACT:IN:" + timeStamp + ":"+QString::number(1));

                                    socket->writeDatagram(Data, QHostAddress("127.0.0.1"), 20022);
                                    //QString tagImgFn("20160718/"+ "_OUT" + ".jpg"); // increase with number
                                    //cv::imwrite(tagImgFn.toStdString(), image);
                                    QFile file(fileName);

                                    if (file.open(QIODevice::Text | QIODevice::Append)) {
                                        QTextStream fileStream(&file);
                                        fileStream << timeStamp+ " ";
                                        fileStream << "PM POLLEN IS IN" << endl;
                                    }

                                    file.close();

                                }//end if
                            }//end if

                            // std::cout<<"Y:="<<tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].y<<std::endl;

                            if((abs(distance)>MOVE_DISTANCE)&&(abs(tracker.tracks[i]->trace[0].y)<abs(tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].y))&&(abs(tracker.tracks[i]->trace[tracker.tracks[i]->trace.size()-1].y)>400)&&(BeeIds==1))
                            {
                                if((!tracker.tracks[i]->is_out)&&(!tracker.tracks[i]->is_bee))
                                {

                                    //                      outF <<currentDateTime()<<" IS OUT"<<std::endl;


                                    tracker.tracks[i]->is_out=true;
                                    tracker.tracks[i]->is_pollen = true;
                                    std::cout<<currentDateTime()<<"POLLEN IS OUT"<<std::endl;
                                    putText(frame, "POLLEN OUT", cv::Point2f(500, 390), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.0, Colors[1]);
                                    // Yolo_array.clear();

                                    QDateTime dateTime = QDateTime::currentDateTime();
                                    QString timeStamp = dateTime.toString("yyyy-MM-dd.hh:mm:ss");
                                    //ui->trackListWidget->addItem(timeStamp);
                                    //ui->trackListWidget->addItem("IS OUT");
                                    ////////////////////////////////////////////////////////////
                                    // Added by Dan 06/13/2016
                                    // Updated 06/23/2016 - added temp+hum

                                    // format: HIVE#:BEE_TAG:ACTION:VALUE:DB_ID
                                    QByteArray Data;

                                    // Added by Dan 06/17/2017
                                    dbNumber = ui->dbBox->text().toInt();
                                    hiveNumber = ui->hiveBox->text().toInt();

                                    // HIVE#
                                    //     Data.append(QString::number(hiveNumber) + ":" + timeStamp + ":IN:" + temperature + ":" + humidity + ":" + QString::number(dbNumber) + ":");
                                    Data.append("B:ACT:OUT:" + timeStamp + ":" +QString::number(1));

                                    socket->writeDatagram(Data, QHostAddress("127.0.0.1"), 20022);
                                    //QString tagImgFn("20160718/"+ "_OUT" + ".jpg"); // increase with number
                                    //cv::imwrite(tagImgFn.toStdString(), image);
                                    QFile file(fileName);

                                    if (file.open(QIODevice::Text | QIODevice::Append)) {
                                        QTextStream fileStream(&file);
                                        fileStream << timeStamp+ " ";
                                        fileStream << "PM POLLEN IS OUT" << endl;
                                    }

                                    file.close();
                                } //end if

                            }//end if






                        }

                    }
                }//
            }

        }








       cv::line(frame, Point( 50, 50 ), Point( 650, 50 ), Colors[1], 2, CV_AA);
       cv::line(frame, Point( 50, 400 ), Point( 650, 400 ), Colors[2], 2, CV_AA);

        //video.write(frame);

        cv::imshow("Tracking Result", frame);

        cv::waitKey(1);
    }
    return 0;
    capture.release();
}

void MainWindow::on_checkBox_useGPU_clicked()
{
    setUseGPU(ui->checkBox_useGPU->isChecked());
}
int MainWindow::findCandidate(int a[], int size)
{
    int maj_index = 0, count = 1;
    for (int i = 1; i < size; i++)
    {
        if (a[maj_index] == a[i])
            count++;
        else
            count--;
        if (count == 0)
        {
            maj_index = i;
            count = 1;
        }
    }
    return a[maj_index];
}
