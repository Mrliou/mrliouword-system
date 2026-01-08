/**
 * atom_t - MrLiouWord 40-byte 原子粒子結構
 * 
 * 核心理念：怎麼過去，就怎麼回來
 * 
 * Author: MR.liou
 */

#ifndef ATOM_T_H
#define ATOM_T_H

#include <stdint.h>

// 角色定義
typedef enum {
    AR_SYS  = 0,  // 系統
    AR_USR  = 1,  // 使用者
    AR_AST  = 2,  // 助手
    AR_TOOL = 3   // 工具
} AtomRole;

// 40-byte 原子結構（緊湊封裝）
typedef struct __attribute__((packed)) {
    uint64_t mid;        // 訊息 ID 雜湊 (8 bytes)
    uint64_t ts;         // 時間戳 (8 bytes)
    uint32_t role;       // 角色 (4 bytes)
    uint32_t n;          // 內容長度 (4 bytes)
    uint64_t content_h;  // 內容精確雜湊 (8 bytes)
    uint64_t sim_h;      // SimHash64 語意指紋 (8 bytes)
} atom_t;  // 總計 40 bytes

// δP₀ 最小狀態變化量
typedef struct {
    uint64_t delta_simhash;
    uint64_t delta_ts;
    uint32_t delta_context;
} delta_p0_t;

// 粒子狀態
typedef enum {
    PARTICLE_ALIVE  = 0,  // 活躍（有熵流動）
    PARTICLE_FROZEN = 1,  // 凍結（可恢復）
    PARTICLE_DEAD   = 2   // 死亡（僅可追溯）
} ParticleState;

// 頻率層級
static const double SCHUMANN = 7.83;
static const double PHI = 1.618033988749895;

static inline double get_layer_freq(int layer) {
    if (layer < 0) return SCHUMANN / PHI;  // L0
    return SCHUMANN * pow(PHI, layer);      // L1-L7
}

// 創建原子
static inline atom_t atom_create(
    uint64_t mid,
    uint64_t ts,
    AtomRole role,
    uint32_t content_len,
    uint64_t content_hash,
    uint64_t simhash
) {
    atom_t a = {
        .mid = mid,
        .ts = ts,
        .role = (uint32_t)role,
        .n = content_len,
        .content_h = content_hash,
        .sim_h = simhash
    };
    return a;
}

// 計算 δP₀
static inline int is_same_particle(atom_t* a, atom_t* b, int threshold) {
    // Hamming 距離計算
    uint64_t xor_sim = a->sim_h ^ b->sim_h;
    int hamming = 0;
    while (xor_sim) {
        hamming += xor_sim & 1;
        xor_sim >>= 1;
    }
    return hamming <= threshold;  // 預設 threshold = 3
}

#endif // ATOM_T_H
