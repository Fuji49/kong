#Kong API
# codes/view.py にある app という変数を呼び出す。
# app には Flask モジュールが提供している flask クラスから作り出されたインスタンスが代入される。
from codes.kongapi import app

# run.py がモジュールとして呼び出されたときは
# __name__ = run.py となり app は実行されない。
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


