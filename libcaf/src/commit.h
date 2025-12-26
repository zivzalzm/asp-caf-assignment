#ifndef COMMIT_H
#define COMMIT_H

#include <string>
#include <ctime>
#include <vector>

class Commit {
public:
    /* Immutable commit metadata*/
    const std::string tree_hash;  // Hash of the tree object
    const std::string author;     // Author of the commit
    const std::string message;    // Commit message
    const std::time_t timestamp;  // Timestamp of the commit

    /* Commit parents (ordered)
     * parents[0] is considered the primary (HEAD) parent*/
    const std::vector<std::string> parents; // Parent commit hash

    // Root commit (no parents)
    Commit(const std::string& tree_hash,
           const std::string& author,
           const std::string& message,
           std::time_t timestamp);

    // Regular commit (single parent)
    Commit(const std::string& tree_hash,
           const std::string& parent,
           const std::string& author,
           const std::string& message,
           std::time_t timestamp);

    // Merge commit (multiple parents)
    Commit(const std::string& tree_hash,
           const std::vector<std::string>& parents,
           const std::string& author,
           const std::string& message,
           std::time_t timestamp);

    // --- Accessors ---

    const std::vector<std::string>& get_parents() const;
    const std::string& get_primary_parent() const;
};

#endif // COMMIT_H
