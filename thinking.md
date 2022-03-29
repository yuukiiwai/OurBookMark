# 考え事リスト
## 辞書リストの比較
### 理由
辞書リストはset(list)で集合化出来ないので
### 扱うデータの形
ASM = [A,B,C,...]  
A = [{url:a},{url:b},{url:c},...]  
B = [{url:b},{url:d},{url:a},...]  
C = [{url:b},{url:d},{url:c},...]  
### 出力形
RES = [b,...]  
A,B,Cに共通するもの
### 手順1 ボツ
データ複製  
ASM, ASM_copy  
比較
1. ASMからAを取り出してASM_copyのAと比較(以後コピーを'で記述)  
1. AとB'の共通部を記述(例:{url:a},{url:b}) -> tempに保存
1. tempとC'の共通部を記述(例:{url:b}) -> tempに再代入
1. tempとD'の...  
1. 最後まで  

つまり、ASM_copyじゃなくてASM[0]とASM[1]~[len(ASM)-1]までを比較する？
### 手順2
収集するリスト変数 temp=[]  
zero = ASM[0]  
other = ASM[1:]  
**条件** 
* len(ASM) >= 2  

**手順**
1. temp = zero
1. tempとother[0]の共通部をtempに保存
1. tempとother[1]の共通部をtempに保存
1. otherが尽きるまで  

**tempとother[n]の共通部の探し方**  
**条件**  
temp = [{a},{b},{c},{d},{e},{f}...]
other[n] = [{b},{c},{f}]  
**手順**  
1. tempから１つずつ取ってきて、(a in other[n])を確かめる  
1. temp2=[]に確かめたものをappendする
1. tempが尽きたらtemp = temp2
1. temp2をclearする

---
## 詳細タグの扱い
