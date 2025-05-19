"""
The following are small snippets of private repository code.
While these projects cant paint a full example, I hope it can
demonstrate my prefered approaches to scenarios within python.
"""

//  StartCamera.h
//  testCV
//
//  Created by Mason Kirby on 8/27/22.
//

#include <iostream>
#include <opencv2/core.hpp>
#include <opencv2/core.hpp>
#include <opencv2/face.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/objdetect.hpp>
#include <opencv2/imgproc.hpp>
#include <vector>
#include <unistd.h>
#include <string>

using namespace std;
using namespace cv;
using namespace cv::face;



#ifndef StartCamera_h
#define StartCamera_h

CascadeClassifier faceDetect;
string name;
string fileName;
int fileNumber;
int numOfFiles = 0;


void detectAndDisplay(Mat &frame){
    
    vector<Rect> faces;
    Mat grey_frame;
    Mat crop;
    Mat res;
    Mat grey;
    string text;
    stringstream sstm;
    
    cvtColor(frame, grey_frame, COLOR_BGR2GRAY);
    equalizeHist(grey_frame, grey_frame);
    
    faceDetect.detectMultiScale(grey_frame, faces, 1.1, 2, 0 | CASCADE_SCALE_IMAGE, Size(30, 30));
    
    Rect roi_b;
    Rect roi_c;
    
    size_t ic = 0;
    int ac = 0;
    
    size_t ib = 0;
    int ab = 0;
    

    for(int ic = 0; ic < faces.size(); ic++)
        {
              roi_c.x = faces[ic].x;
              roi_c.y = faces[ic].y;
              roi_c.width =  (faces[ic].width);
              roi_c.height = (faces[ic].height);
            
            ac = roi_c.width * roi_c.height;
            
            roi_b.x = faces[ib].x;
            roi_b.y = faces[ib].y;
            roi_b.width =  (faces[ib].width);
            roi_b.height = (faces[ib].height);


//            rectangle(image, Point(x1, y1), Point(x2,y2), Scalar(50, 50, 255), 3);
//
//            putText(image, to_string(faces.size()), Point(10,40), FONT_HERSHEY_COMPLEX, 1, Scalar(255,255,255), 1);
            
            crop = frame(roi_b);
            resize(crop, res, Size(128,128), 0, 0, INTER_LINEAR);
            cvtColor(crop, grey, COLOR_BGR2GRAY);
            stringstream ssfn;
            fileName = "/Users/masonkirby/Desktop/Faces";
            ssfn << fileName.c_str() << name << fileNumber << ".jpg";
            fileName = ssfn.str();
            imwrite(fileName, res);
            fileNumber++;
            
        }
}

// Start a camera and add photos of the face to a folder to be retrieved later
// retrieve photos inorder to train the model 
void addFace(){
    
    cout << "enter your name" << endl;
    cin >> name;
    VideoCapture cap(0);
    
    if(!faceDetect.load("/Users/masonkirby/Desktop/face.xml")){
        cout << "Error" << endl;
        return;
    }
    
    Mat frame;
    cout << "Capturing your face 10 times, press c 10 times keeping you facec in front of the camera" << endl;
    
    char key;
    int i = 0;
    
    for(;;){
        
        cap >> frame;
        imshow("Frame", frame); 
        detectAndDisplay(frame);
        i++;
        if(i == 10){
            cout << "Face added!" << endl;
            break;
        }
        
        waitKey(1000);
       
    }
    
    return;
}

// dbread is Data base read. It is how the photos are going to populate the vectors
//
static void dbread(vector<Mat>& images, vector<int>& labels){
    vector<cv::String> fn;
    fileName = "/Users/masonkirby/Desktop/Faces2/";
    
    glob(fileName, fn, false);
    
    size_t count = fn.size();
    
    string itsname = "";
    char sep;
    
    for(size_t i = 0; i < count; i++){
        itsname ="";
        sep = '\\';
        size_t j = fn[i].rfind(sep, fn[i].length());
        if(j != string::npos)
        {
            itsname=(fn[i].substr(j+1, fn[i].length() - j-6));
        }
        images.push_back(imread(fn[i],0));
        labels.push_back(atoi(itsname.c_str()));
    }
    
}

// place the vector of photos inside of the machine learning alogrithm named EigenFaceRecognizer.train
void eigenFaceTrainer(){
    vector<Mat> images;
    vector<int> labels;
    dbread(images, labels);
    
    Ptr<EigenFaceRecognizer> model = EigenFaceRecognizer::create();
    
    model->train(images, labels);
    
    model->save("/Users/masonkirby/Desktop/Faces2/eigenFace.yml");
    
    cout << "Tarining Complete" << endl;
    waitKey(10000);
}

void faceRecognizer(){
    Ptr<EigenFaceRecognizer> model = EigenFaceRecognizer::create();
    
    model->read("/Users/masonkirby/Desktop/Faces2/eigenFace.yml");
    
    Mat testSample = imread("/Users/masonkirby/Desktop/Faces2/FACESMason0.jpg",0);
    
    int img_width = testSample.cols;
    int img_height = testSample.rows;
    
    string windows = "Capture - face detection";
    
    if(!faceDetect.load("/Users/masonkirby/Desktop/face.xml")){
        cout << "Error" << endl;
        return;
    }
    
    VideoCapture cap(0);
    
    if(!cap.isOpened()){
        cout << "exit" << endl;
        return;
    }
    namedWindow(windows, 1);
    long count = 0;
    string Pname = "";
    
    while(true)
    {
        vector<Rect> faces;
        Mat frame, crop;
        Mat grayScaleFrame;
        Mat Original;
        string name;
        
        cap >> frame;
        
        // count frames
        count = count + 1;
        
        if(!frame.empty())
        {
            //clone from original frame
            Original = frame.clone();
            
            // convert image to gray scale and equalize
            cvtColor(Original, grayScaleFrame, COLOR_BGR2GRAY);
            
            
            // detect face in gray images
            faceDetect.detectMultiScale(grayScaleFrame, faces, 1.1, 3, 0, cv::Size(70,70));
            
            //number of faces in gray image
            string fameset = to_string(count);
            string faceset = to_string(faces.size());
            
            int width, height = 0;
            
            for(int i = 0; i < faces.size(); i++)
            {
                Rect face_i = faces[i];
                
                Mat face = grayScaleFrame(face_i);
                
                Mat face_resized;
                
                resize(face, face_resized, Size(img_width, img_height), 1.0, 1.0, INTER_CUBIC);
                
                int label = -1; double confidence = 0;
                
                model->predict(face_resized, label, confidence);
                
                cout << "Confidence: " << confidence << " Label " << label << endl;
                
                Pname = to_string(label);
                
                rectangle(Original, face_i, CV_RGB(0, 255, 0), 1);
                
                name = "Mason";
                
                int pos_x = max(face_i.tl().x - 10, 0);
                int pos_y = max(face_i.tl().y - 10, 0);
                
                // name the person who is in the image
                putText(Original, name, Point(pos_x,pos_y), FONT_HERSHEY_COMPLEX_SMALL, 1.0, CV_RGB(0,255, 0), 1.0);
                
            }
            imshow(windows, Original);
            
        }
        if(waitKey(30) >= 0) break;
        
    }
    
}

#endif /* StartCamera_h */


// Base class for rendering objects
class Renderable {
public:
    virtual void draw() const = 0; // Virtual function for drawing
    virtual ~Renderable() {}
};

// Cube class
class Cube : public Renderable {
private:
    float vertices[72];
    unsigned int indices[36];

public:
    Cube() {
        // Define vertices for a cube
        float* heapVertices = new float[72]{
            // Front face
           -0.5f, -0.5f,  0.5f,  // Bottom-left
            0.5f, -0.5f,  0.5f,  // Bottom-right
            0.5f,  0.5f,  0.5f,  // Top-right
           -0.5f,  0.5f,  0.5f,  // Top-left

            // Back face
           -0.5f, -0.5f, -0.5f,  // Bottom-left
            0.5f, -0.5f, -0.5f,  // Bottom-right
            0.5f,  0.5f, -0.5f,  // Top-right
           -0.5f,  0.5f, -0.5f,  // Top-left
        };

        // Copy vertices to the member array
        std::copy(heapVertices, heapVertices + 72, vertices);
        delete[] heapVertices; // Clean up heap memory

        // Define indices for the cube
        unsigned int tempIndices[36] = {
            // Front face
            0, 1, 2,  2, 3, 0,
            // Back face
            4, 5, 6,  6, 7, 4,
            // Left face
            0, 4, 7,  7, 3, 0,
            // Right face
            1, 5, 6,  6, 2, 1,
            // Top face
            3, 7, 6,  6, 2, 3,
            // Bottom face
            0, 1, 5,  5, 4, 0
        };

        std::copy(tempIndices, tempIndices + 36, indices);
    }

    void draw() const override {
        glEnableClientState(GL_VERTEX_ARRAY);
        glVertexPointer(3, GL_FLOAT, 0, vertices);

        glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, indices);

        glDisableClientState(GL_VERTEX_ARRAY);
    }
};

std::atomic<float> rotationAngle = 0.0f; // Shared rotation angle

// Function to update the rotation angle in a separate thread
void updateRotation() {
    while (true) {
        rotationAngle += 0.01f;
        if (rotationAngle > 360.0f)
            rotationAngle = 0.0f;
        std::this_thread::sleep_for(std::chrono::milliseconds(16)); // ~60 FPS
    }
}



using namespace std; 

class twoDArray{
    int userInputN, userInputM, userInputS, userInputT; 
    int** first_array;
    int** second_array;
    int** third_array; 
public: 
    twoDArray(){
        userInputM = 0; 
        userInputN = 0;
        userInputT = 0; 
        userInputS = 0; 
    }
    twoDArray(int m, int n, int s, int t){
        userInputM = m; 
        userInputN = n;
        userInputS = s;
        userInputT = t; 
    }

    ~twoDArray(){ 

        delete first_array; 
        delete second_array; 
        delete third_array; 

    }
    void createArray();
    void multiplyArray(); 
    void printArrays(); 

}; 
void twoDArray::createArray(){
    //creating the first 2 2d arrays determined by the size of the user inputs
    
    first_array = new int*[userInputM];
    second_array = new int*[userInputS]; 
      
    for(int i = 0; i < userInputM; i++){
        first_array[i] = new int[userInputN];
    }
    for(int i = 0; i < userInputS; i++){
        second_array[i] = new int[userInputT];
    }
    //populating the arrays with index numbers 
    for(int i = 0; i < userInputM; i++){
        for(int j = 0; j< userInputN; j++){
            first_array[i][j] = i + j; 
            second_array[i][j] = i + j;     
        }
        cout << endl; 
    }
    //creating the third array size out of inputs from the first two arrays 
    third_array = new int*[userInputM];
    for(int i = 0; i < userInputM; i++){
        third_array[i] = new int[userInputT];
    }
}
void twoDArray::multiplyArray(){
       //mutiplying the two arrays to make a third one
       for(int i = 0; i < userInputM; i++){
         for(int j = 0; j< userInputT; j++){
             for(int k = 0; k < userInputS; k++){
                //multiplying the first 2 arrays 
                third_array[i][j] += first_array[i][k] * second_array[k][j];  
              }   
           }
        }  
}

void twoDArray::printArrays(){

    // Print first array
        cout << "the first array: " << endl; 
        for(int i = 0; i < userInputM; i++){
            for(int j = 0; j< userInputN; j++){
                cout << first_array[i][j] << " ";    
            }
            cout << endl; 
        }
        // print second array
        cout << "the second array: " << endl; 
        for(int i = 0; i < userInputM; i++){
            for(int j = 0; j< userInputN; j++){
                cout << second_array[i][j] << " ";    
            }
            cout << endl; 
        }
        //print third array 
        cout << "the third array: " << endl; 
        for(int i = 0; i < userInputM; i++){
            for(int j = 0; j< userInputT; j++){
                cout << third_array[i][j] << " ";    
            }
            cout << endl; 
        }
    }

// threaded_task_queue.cpp
// Demonstrates multithreading and synchronization using std::thread, std::mutex, and std::condition_variable

#include <iostream>
#include <thread>
#include <mutex>
#include <queue>
#include <condition_variable>
#include <functional>
#include <vector>
#include <atomic>

class TaskQueue {
public:
    void push(std::function<void()> task) {
        std::lock_guard<std::mutex> lock(mutex_);
        tasks_.push(task);
        cv_.notify_one();
    }

    void start(size_t threads = 2) {
        running_ = true;
        for (size_t i = 0; i < threads; ++i) {
            workers_.emplace_back([this] { worker(); });
        }
    }

    void stop() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            running_ = false;
        }
        cv_.notify_all();
        for (auto& t : workers_) {
            if (t.joinable()) {
                t.join();
            }
        }
    }

    ~TaskQueue() {
        stop();
    }

private:
    void worker() {
        while (true) {
            std::function<void()> task;

            {
                std::unique_lock<std::mutex> lock(mutex_);
                cv_.wait(lock, [this] { return !tasks_.empty() || !running_; });

                if (!running_ && tasks_.empty()) {
                    return;
                }

                task = std::move(tasks_.front());
                tasks_.pop();
            }

            task();
        }
    }

    std::queue<std::function<void()>> tasks_;
    std::vector<std::thread> workers_;
    std::mutex mutex_;
    std::condition_variable cv_;
    bool running_ = false;
};

int main() {
    TaskQueue queue;
    queue.start(4);

    for (int i = 0; i < 10; ++i) {
        queue.push([i]() {
            std::cout << "Running task " << i << std::endl;
        });
    }

    std::this_thread::sleep_for(std::chrono::seconds(1));
    queue.stop();

    return 0;
}
