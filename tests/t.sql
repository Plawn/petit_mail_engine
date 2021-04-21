select
    i.id,
    i.remaning
from
    (
        SELECT
            s.*,
            s.quota - s.pending - (
                select
                    count(e.*)
                from
                    email e
                    join sender s on s.id = e.sender
                where
                    age(e.sent_at) < '24h'
            ) as remaning
        FROM
            sender s
            JOIN identity i on i.id = s.identity
        where
            i.id = 1
        group by
            s.id
    ) as i
where
    remaning > 0;