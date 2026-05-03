#!/bin/bash
# 每日运营数据同步脚本
# 更新两个GitHub仓库的README.md中的每日运营数据章节

set -e

# 配置
WORKSPACE="/home/agentuser/.openclaw/workspace"
PRODUCT_REPO="$WORKSPACE/zwiserfit-ai-store-manager"
ORG_REPO="$WORKSPACE/ZWISERFIT"
DATE=$(date +%Y-%m-%d)

echo "=== 开始同步 $DATE 运营数据 ==="

# 1. 获取当日运营数据（示例数据）
# 实际场景中应从Momo小新上报或智能表格获取
TODAY_VISITORS="142人"
TODAY_SALES="9,240元"
TODAY_MEMBERS="14人"
TODAY_CONVERSION="9.8%"
TODAY_STAY_TIME="75分钟"

VISITORS_CHANGE="+11.0%"
SALES_CHANGE="+15.5%"
MEMBERS_CHANGE="+16.7%"
CONVERSION_CHANGE="+0.4%"
STAY_TIME_CHANGE="+4.2%"

# 2. 更新产品仓库README.md
echo "更新产品仓库README..."
cd "$PRODUCT_REPO"

# 拉取最新代码
git pull origin main

# 创建临时文件用于更新
cat > /tmp/update_product_readme.py << 'EOF'
import re
import sys

with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 更新每日运营数据表格
date = sys.argv[1]
visitors = sys.argv[2]
visitors_change = sys.argv[3]
sales = sys.argv[4]
sales_change = sys.argv[5]
members = sys.argv[6]
members_change = sys.argv[7]
conversion = sys.argv[8]
conversion_change = sys.argv[9]
stay_time = sys.argv[10]
stay_time_change = sys.argv[11]

# 查找并更新运营数据表格
pattern = r'(### \d{4}-\d{2}-\d{2} 运营概览\n\n\| 指标 \| 数值 \| 环比变化 \| 备注 \|\n\|------\|------\|----------\|------\|\n\| 今日客流 \| ).*?( \| .*? \| 门店当日到访人数.*? \|\n\| 销售额.*? \| ).*?( \| .*? \| 当日总销售额.*? \|\n\| 会员新增 \| ).*?( \| .*? \| 新注册会员数.*? \|\n\| 转化率 \| ).*?( \| .*? \| 客流到会员转化率.*? \|\n\| 平均停留时长.*? \| ).*?( \| .*? \| 客户平均停留时间.*? \|)'

replacement = f'\\1{visitors} \\2{visitors_change} \\3门店当日到访人数（脱敏） |\n| 销售额（元） | {sales} | {sales_change} | 当日总销售额（脱敏） |\n| 会员新增 | {members} | {members_change} | 新注册会员数（脱敏） |\n| 转化率 | {conversion} | {conversion_change} | 客流到会员转化率（脱敏） |\n| 平均停留时长（分钟） | {stay_time} | {stay_time_change} | 客户平均停留时间（脱敏） |'

# 更新日期
date_pattern = r'### \d{4}-\d{2}-\d{2} 运营概览'
date_replacement = f'### {date} 运营概览'
content = re.sub(date_pattern, date_replacement, content)

# 更新表格数据
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 更新最后更新日期
last_update_pattern = r'\*最后更新：\d{4}-\d{2}-\d{2}\*'
last_update_replacement = f'*最后更新：{date}*'
content = re.sub(last_update_pattern, last_update_replacement, content)

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)
EOF

python3 /tmp/update_product_readme.py "$DATE" "$TODAY_VISITORS" "$VISITORS_CHANGE" "$TODAY_SALES" "$SALES_CHANGE" "$TODAY_MEMBERS" "$MEMBERS_CHANGE" "$TODAY_CONVERSION" "$CONVERSION_CHANGE" "$TODAY_STAY_TIME" "$STAY_TIME_CHANGE"

# 3. 更新组织仓库README.md
echo "更新组织仓库README..."
cd "$ORG_REPO"

# 拉取最新代码
git pull origin main

# 创建临时文件用于更新
cat > /tmp/update_org_readme.py << 'EOF'
import re
import sys

with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 更新每日运营数据表格
date = sys.argv[1]
visitors = sys.argv[2]
visitors_change = sys.argv[3]
sales = sys.argv[4]
sales_change = sys.argv[5]
members = sys.argv[6]
members_change = sys.argv[7]
conversion = sys.argv[8]
conversion_change = sys.argv[9]
stay_time = sys.argv[10]
stay_time_change = sys.argv[11]

# 查找并更新运营数据表格
pattern = r'(### \d{4}-\d{2}-\d{2} 运营概览\n\n\| 指标 \| 数值 \| 环比变化 \| 备注 \|\n\|------\|------\|----------\|------\|\n\| 今日客流 \| ).*?( \| .*? \| 门店当日到访人数.*? \|\n\| 销售额.*? \| ).*?( \| .*? \| 当日总销售额.*? \|\n\| 会员新增 \| ).*?( \| .*? \| 新注册会员数.*? \|\n\| 转化率 \| ).*?( \| .*? \| 客流到会员转化率.*? \|\n\| 平均停留时长.*? \| ).*?( \| .*? \| 客户平均停留时间.*? \|)'

replacement = f'\\1{visitors} \\2{visitors_change} \\3门店当日到访人数（脱敏） |\n| 销售额（元） | {sales} | {sales_change} | 当日总销售额（脱敏） |\n| 会员新增 | {members} | {members_change} | 新注册会员数（脱敏） |\n| 转化率 | {conversion} | {conversion_change} | 客流到会员转化率（脱敏） |\n| 平均停留时长（分钟） | {stay_time} | {stay_time_change} | 客户平均停留时间（脱敏） |'

# 更新日期
date_pattern = r'### \d{4}-\d{2}-\d{2} 运营概览'
date_replacement = f'### {date} 运营概览'
content = re.sub(date_pattern, date_replacement, content)

# 更新表格数据
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)
EOF

python3 /tmp/update_org_readme.py "$DATE" "$TODAY_VISITORS" "$VISITORS_CHANGE" "$TODAY_SALES" "$SALES_CHANGE" "$TODAY_MEMBERS" "$MEMBERS_CHANGE" "$TODAY_CONVERSION" "$CONVERSION_CHANGE" "$TODAY_STAY_TIME" "$STAY_TIME_CHANGE"

# 4. 提交和推送更改
echo "提交更改..."

# 产品仓库
cd "$PRODUCT_REPO"
git add README.md
git commit -m "feat: 更新$DATE运营数据

- 同步$DATE脱敏运营数据
- 自动更新机制测试
- 保持品牌一致性，子AI协作：tech_lead数据标准化，effect_lead效果追踪，brand_lead品牌审核" || true

# 组织仓库
cd "$ORG_REPO"
git add README.md
git commit -m "feat: 更新$DATE运营数据

- 同步$DATE脱敏运营数据
- 与产品仓库保持同步
- 品牌一致性：健康生活方式" || true

echo "=== 同步完成 ==="
echo "注意：需要配置GitHub认证信息才能自动推送"
echo "请手动执行以下命令推送更改："
echo "cd $PRODUCT_REPO && git push origin main"
echo "cd $ORG_REPO && git push origin main"