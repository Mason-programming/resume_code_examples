#pragma once 
#include <efsw/efsw.hpp>
#include <iostream>
#include <unordered_map>
#include <queue>
#include <vector> 


class UpdateListener : public efsw::FileWatchListener {
  public:
    void handleFileAction( efsw::WatchID watchid, const std::string& dir,
                           const std::string& filename, efsw::Action action,
                           std::string oldFilename ) override {
        switch ( action ) {
            case efsw::Actions::Add:
                std::cout << "DIR (" << dir << ") FILE (" << filename << ") has event Added"
                          << std::endl;

                whatToWatch()
                break;
            case efsw::Actions::Delete:
                std::cout << "DIR (" << dir << ") FILE (" << filename << ") has event Delete"
                          << std::endl;
                break;
            case efsw::Actions::Modified:
                std::cout << "DIR (" << dir << ") FILE (" << filename << ") has event Modified"
                          << std::endl;
                

                break;
            case efsw::Actions::Moved:
                std::cout << "DIR (" << dir << ") FILE (" << filename << ") has event Moved from ("
                          << oldFilename << ")" << std::endl;
                break;
            default:
                std::cout << "Should never happen!" << std::endl;
        }
    }

    std::string whatToWatch(std::unordered_map<std::string, efsw::WatchID>& filesToWatch; std::string filePath; std::string& department); 

    std::string sendCode(std::string& test); 

    reindexing(std::unordered_map<std::string, efsw::WatchID>& filesToWatch); 
};



