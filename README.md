# CGI calculator scheme/RDB(gauche/postgresql)
自分で調べられるようになったほうがいい。

* cgi: [calc.cgi](http://c104.melt.kyutech.ac.jp:8080/~hkim/calc/calc.cgi)
* source: [calc.html](http://c104.melt.kyutech.ac.jp:8080/~hkim/calc/calc.html)
* table: [create.html](http://c104.melt.kyutech.ac.jp:8080/~hkim/calc/create.html)

## Gauche から Postgres へのコネクションの取り方

pg_hba.conf をよく読む。hbaは host base authentication の略だそうな。

vm2014 では `/etc/postgresql/9.3/main/pg_hba.conf` にある。

```
local   all             all                                     trust
```

の trust の部分は vm2014 にアカウントを持つユーザは信用するという意味で、
ローカルから postgresql にそのアカウント名でアクセスしてきたら許可する。
trust を md5 に変えると、psql で作成したユーザ名+パスワードで認証できるようだ。
peer とあったらホストマシンの認証を受けるということ。
postgres ユーザは認証が peer になっている。

postgre のユーザはユーザ名のデータベースのオーナーとなる（のか、
そういう風に hkim が vm2014 に仕組んだのか、忘れてしまったが）ので、
vm2014 上で calculator を動かすには、

```scheme
(define *conn* (dbi-connect "dbi:pg" :username "hkim"))
```

## ファイルを分離するべきか

学生はファイルを分けてプログラミングすることを覚えるべき。

だが、教条主義的にソースコードをぶつ切りにするのはどうかな？
機能を交通整理し、適切な関数に分担させることをファイルの分離よりも重視すべき。
関数名にも神経を使おう。

今回は自分で書くコードは calc.cgi ひとつにまとめる。
もちろん必要なライブラリは require する。
現在、130行足らず。

## 失敗したこと

emacs で gosh 動かし、プログラムを作ったが、
出来上がったはずのコードを vm2014 にアップロードすると動かない。

理由がわからず、ローカルに http サーバ立ち上げ、 cgi 呼び出してみると動かない。「出来上がった」が誤解だった。

理由は突き止めてみるとかなり自明（と簡単に書いているが、見つけるまで時間はかかった。未熟者だ）で、
cgi プログラムの最初の方に、

```scheme
(define db-close (dbi-close *conn*))
```

と書いていたのが原因。

開発中は定義した関数を emacs 中で eval し、動作確認するが、
そのデータベースとのコネクションを切る部分は意識的に評価を避けていた。

```scheme
(define dbi-close (lambda () (db-close (dbi-close *conn*))))
```

この年になってこういう腐ったミスもやる。
学生はおれ以上にプログラム書け。そうしないと経験しないし、覚えない。

## 失敗したこと

今回のデザインは db を単にセッションを越えて保持されるメモリとして使うこと。
それなのに update すべきところを insert してデータベースの行を増やしていた。
プログラムは行が複数あるとは思ってないから、そのままだったらそのうち実行時エラーだった。
psql でモニタするまで気がつかなかった。イージーミス。

## 失敗したこと

その他にもはずかしい小さいミスはたくさん。書いてみないと覚えない。

----
written by hkimura, 2014-09-13.
