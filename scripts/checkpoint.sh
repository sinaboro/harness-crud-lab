#!/bin/sh
# ============================================================
# checkpoint.sh - 교시별 "완성 예시"를 작업 폴더로 가져오는 스크립트
#
# 실습이 막혔거나 결석해서 앞 교시 결과가 없을 때 쓴다.
# checkpoints/lessonNN 의 app, tests 폴더로 내 app, tests 폴더를 "바꿔치기"한다.
#
# 실행 (dev 컨테이너 안에서):
#   sh scripts/checkpoint.sh 08          # 8교시를 마친 상태로 맞춘다
#   sh scripts/checkpoint.sh 08 --force  # 저장 안 한 변경이 있어도 덮어쓴다
# ============================================================

set -e

lesson="$1"
force="$2"
source_dir="checkpoints/lesson$lesson"

# 1) 번호를 안 줬거나 그런 체크포인트가 없으면 사용법을 보여 준다.
if [ -z "$lesson" ] || [ ! -d "$source_dir" ]; then
    echo "사용법: sh scripts/checkpoint.sh <교시 번호> [--force]"
    echo "가져올 수 있는 체크포인트:"
    ls checkpoints | sed 's/lesson/  /'
    exit 1
fi

# 2) 저장(commit)하지 않은 변경이 있으면 멈춘다. (내 작업이 사라지는 사고 방지)
if [ "$force" != "--force" ] && [ -n "$(git status --porcelain app tests)" ]; then
    echo "app, tests 폴더에 저장하지 않은 변경이 있습니다."
    echo "먼저 커밋하거나, 버려도 된다면 --force 를 붙여 다시 실행하세요."
    exit 1
fi

# 3) 바꿔치기
rm -rf app tests
cp -r "$source_dir/app" app
cp -r "$source_dir/tests" tests

echo "$source_dir 의 app, tests 를 가져왔습니다."
echo "확인: sh scripts/verify.sh"
