#include "fileWatcher.h"

std::string UpdateListener::whatToWatch(std::unordered_map<std::string, efsw::WatchID>& filesToWatch; std:string filePath; std::string& department){ 

    // Add a folder to watch, and get the efsw::WatchID
    // It will watch the /tmp folder recursively ( the third parameter indicates that is recursive )
    // Reporting the files and directories changes to the instance of the listener

    //implment priotrity qeue 



    efsw::WatchID watchID = fileWatcher->addWatch(filePath, listener, true);

    


    enum os {windows, darwin, linux}; 

    #ifdef _WIN32 
        std::string f; 

    #elif __linux__

    #elif __APPLE__
    

    // Choose a OS to watch 
    switch (os){ 

        case 


    }

    filesToWatch[watchID] = filePath; 



    return filesToWatch; 
}; 


