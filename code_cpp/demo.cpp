"""
The following are small snippets of private repository code.
While these projects cant paint a full example, I hope it can
demonstrate my prefered approaches to scenarios within python.
"""

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
