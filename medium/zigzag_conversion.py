class Solution:
    def convert(self, s: str, numRows: int) -> str:
        if numRows == 1:
            return s
        length = len(s)
        interval = 2 * (numRows - 1)
        times = int((length - 1) / interval)
        x = times * interval + 1
        if x < length:
            times += 1
            x += interval
            s = s + (x - length) * '*'
        res = s[0]
        for j in range(numRows):
            for i in range(times):
                k = i * interval
                if j != 0:
                    res += s[k + j]
                if j != numRows - 1:
                    res += s[k + interval - j]
        return res.replace('*', '')


# PAHNAPLSIIGYIR
s = Solution().convert('PAYPALISHIRING', 3)
print(s)
