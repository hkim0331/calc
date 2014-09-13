# CGI calculator scheme/RDB(gauche/postgresql)

自分で調べられるようになったほうがいい。

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

学生は分離することを、まず、覚えるべき。

だが、教条主義的にソースコードをぶつ切りにするのはどうかな？
機能を交通整理し、適切な関数に分担させることをもっと重視すべき。
関数名にももっと神経を使おう。

もちろん必要なライブラリは require するが、
今回は自分で書くコードは calc.cgi ひとつにまとめる。現在、130行足らず。

## 失敗したこと

emacs で gosh 動かし、書いた関数の動作を確かめつつ、プログラムを作ったが、
プログラムの最初の方に、

```scheme
(define db-close (dbi-close *conn*))
```

これがプログラムの動作を止めていた。だって、こやつ、関数じゃない。
cgi が呼出され、その直上でせっかく開いた db とのコネクションを切る。
こういう、うっかりミスもやはり、実際にプログラム書かないと経験しない。
覚えない。

```scheme
(define (lambda () (db-close (dbi-close *conn*))))
```

## 失敗したこと

今回のデザインは db を単にセッションを越えて保持されるメモリとして使うこと。
それなのに update すべきところを insert して、データベースの行を増やしていた。
psql でモニタするまで気がつかなかった。イージーミスだなあ。

## 失敗したこと

その他にもはずかしい小さいミスはたくさん。


