#ifndef TREE_H
#define TREE_H

#include <map>
#include <unordered_map>
#include <string>
#include <utility>

#include "tree_record.h"

class Tree {
public:
    const std::map<std::string, TreeRecord> records;

    explicit Tree(const std::map<std::string, TreeRecord>& records): records(records) {}

    // NEW: constructor from unordered_map (used by Python bindings)
    explicit Tree(const std::unordered_map<std::string, TreeRecord>& recs)
        : records(recs.begin(), recs.end()) {}


    std::map<std::string, TreeRecord>::const_iterator record(const std::string& key) const {
        return records.find(key);
    }
};

#endif // TREE_H

