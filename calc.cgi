#!/usr/local/bin/gosh
;;-*- mode: scheme; coding: utf-8; -*-
;; programmed by Hiroshi Kimura, 2014-09-13.
;; as an example for melt 2014 students.

(use www.cgi)
(use text.html-lite)
(use gauche.collection)
(use dbi)
(use dbd.pg)

;; must adjust when deploy.
(define *conn* (dbi-connect "dbi:pg" :username "hkim"))
;;;;;;;;;;;;;;;;;;;;;;

(define db-close
  (lambda () (dbi-close *conn*)))

;; sql 文を文字列で受け取り、実行する。戻り値は構造体。
(define exec
  (lambda (sql)
    (dbi-do *conn* sql)))

(define button
  (lambda (key)
     (html:td (html:input :type "submit" :value key :name "v"))))

(define update-view
  (lambda (value)
    ;; value を得るために db-connect するわけで、
    ;; value が得られた今はデータベースをクローズするチャンス。
    (db-close)
    ;;
    (list
     (cgi-header)
     (html-doctype)
     (html:html
      (html:head
       (html:meta :charset "utf-8")
       (html:link :rel "stylesheet" :href "display.css"))
      (html:body
       (html:div :id "calc"
                 (html:p value)
                 (html:form :method "post"
                   (html:table
                    (html:tr (map button '("7" "8" "9" "*")))
                    (html:tr (map button '("4" "5" "6" "-")))
                    (html:tr (map button '("1" "2" "3" "+")))
                    (html:tr (map button '("0" "C" "=" "/")))))))))))

;; ださいを承知で、わかりやすいコードを優先。
;; 押されたキーは演算子か？
(define op?
  (lambda (key)
    (or (string=? "*" key) (string=? "-" key) (string=? "+" key)
        (string=? "/" key))))

;; SQL の戻り値の最初のコラム。get から呼ぶ。
;; デバッグ用に独立した関数としておく。
;; 最初は get の let で定義していた。
(define value
  (lambda (ret)
    (car (map (lambda (x) (dbi-get-value x 0)) ret))
    ))

;; コラムの値を取得する。
;; FIXME
;; getの引数は num1, num2, op しか許さないので
;; get-num1 とか get-num2 のような関数にした方がいいだろう。
(define get
  (lambda (var)
    (let* ((ret (exec (format #f "select ~a from calc;" var)))
           (val (value ret)))
      ;; ださっ。
      (if (string->number val) (string->number val)
          val)
      )))

;; (define get
;;   (lambda (var)
;;     (let* ((ret (exec (format #f "select ~a from calc;" var)))
;;            (val (value ret)))
;;       val
;;       )))

;; (define get-num1
;;   (lambda ()
;;     (string->number (get "num1"))))

;; (define get-num2
;;   (lambda ()
;;     (string->number (get "num2"))))

;; (define get-op
;;   (lambda ()
;;     (get "op")))

;; C が押されたときの動作。
(define clear
  (lambda ()
    (exec "update calc set num1=0, num2=0, op=' ';")
    0
    ))

;; = が押された時、計算を実行する。
(define do-calc
  (lambda ()
    (let ((op (get "op"))
          (num1 (get "num1"))
          (num2 (get "num2")))
      ;; FIXME, 繰り返しのコード。マクロで書く？
      (cond
       ((string=? op "+") (+ num2 num1))
       ((string=? op "-") (- num2 num1))
       ((string=? op "*") (* num2 num1))
       ((string=? op "/") (/ num2 num1)))
      )))

;; +, -, * / が押されたら、num1 の値を num2 にコピー、num1 をリセット。
(define operator
  (lambda (op)
    (exec (format #f "update calc set op='~a';" op))
    (exec (format #f "update calc set num2='~a';" (get "num1")))
    (exec "update calc set num1=0;")
    (get "num2")
    ))

;; 数字が押されたら、num1 をアップデートする。
(define number
  (lambda (key)
    (exec (format #f "update calc set num1='~a';"
                  (+ (* 10 (get "num1")) (string->number key))))
    (get "num1")
    ))

(cgi-main
 (lambda (params)
   (let ((p (cgi-get-parameter "v" params)))
     ;; ださいが。
     (if p
         (cond
          ((string=? "C" p) (update-view (clear)))
          ((string=? "=" p) (update-view (do-calc)))
          ((op? p) (update-view (operator p)))
          (else (update-view (number p))))
     (update-view (clear)))
     )))
