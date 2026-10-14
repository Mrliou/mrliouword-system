"""MrLiouWord 母體模組命名空間。

origin_signature: MrLiouWord

這個檔案的存在是為了讓母體能 import modules.*。在它出現之前，
modules/ 只是一個無套件標記的目錄，而 MRL_SystemA_ParticleLayer.py 用的是
裸模組匯入（from unified_particle import ...），因此從倉庫根執行時會得到
ModuleNotFoundError: No module named 'unified_particle'——模組實際上與母體
錯位，只有 cd 進該目錄才能使用。只新增、不刪除（LAW-2）。
"""
