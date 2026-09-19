"""
accounts/management/commands/seed_data.py
Run: python manage.py seed_data
Creates demo users, modules, assignments, classes, CATs, and attendance records.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed KITI ICT Department with demo data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('🌱  Seeding KITI demo data...'))

        # ── Superuser ─────────────────────────────────────
        if not User.objects.filter(email='admin@kiti.ac.ke').exists():
            User.objects.create_superuser(
                email='admin@kiti.ac.ke',
                password='admin1234',
                full_name='KITI Admin',
                role=User.ADMIN,
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Admin created  (admin@kiti.ac.ke / admin1234)'))

        # ── Lecturers ─────────────────────────────────────
        lecturers_data = [
            ('omondi@kiti.ac.ke',  'Mr. James Omondi',   'Programming & Data Structures',   'KITI-L001'),
            ('njeri@kiti.ac.ke',   'Mrs. Grace Njeri',   'Cybersecurity & Networking',       'KITI-L002'),
            ('mwangi@kiti.ac.ke',  'Mr. Peter Mwangi',   'Database & Cloud',                 'KITI-L003'),
            ('wafula@kiti.ac.ke',  'Ms. Ruth Wafula',    'Web Development',                  'KITI-L004'),
        ]
        lecturers = []
        for email, name, spec, staff_id in lecturers_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'full_name': name,
                    'role': User.LECTURER,
                    'phone': f'072{random.randint(1000000,9999999)}',
                }
            )
            if created:
                user.set_password('lecturer1234')
                user.save()
                from accounts.models import LecturerProfile
                LecturerProfile.objects.create(user=user, staff_id=staff_id, speciality=spec)
                self.stdout.write(f'  ✓ Lecturer: {name}  ({email} / lecturer1234)')
            lecturers.append(user)

        # ── Students ──────────────────────────────────────
        students_data = [
            ('alice@kiti.ac.ke',  'Alice Kamau',       'D012/ICT/2024', 2),
            ('brian@kiti.ac.ke',  'Brian Odhiambo',    'D013/ICT/2024', 2),
            ('carol@kiti.ac.ke',  'Carol Wanjiku',     'D014/ICT/2024', 1),
            ('david@kiti.ac.ke',  'David Mwangi',      'D015/ICT/2024', 1),
            ('eve@kiti.ac.ke',    'Eve Achieng',       'D016/ICT/2024', 2),
            ('frank@kiti.ac.ke',  'Frank Mutua',       'D017/ICT/2024', 1),
            ('grace@kiti.ac.ke',  'Grace Njeri',       'D018/ICT/2024', 2),
            ('henry@kiti.ac.ke',  'Henry Otieno',      'D019/ICT/2024', 1),
        ]
        students = []
        for email, name, reg_no, year in students_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'full_name': name,
                    'role': User.STUDENT,
                    'phone': f'071{random.randint(1000000,9999999)}',
                }
            )
            if created:
                user.set_password('student1234')
                user.save()
                from accounts.models import StudentProfile
                StudentProfile.objects.create(
                    user=user, reg_number=reg_no,
                    course='Diploma ICT', year=year,
                )
                self.stdout.write(f'  ✓ Student: {name}  ({email} / student1234)')
            students.append(user)

        # ── Modules ───────────────────────────────────────
        from courses.models import Module
        modules_data = [
            ('🔐', 'Cybersecurity Fundamentals',     'Network security, ethical hacking, cryptography.', ['Security','Kali Linux','Cryptography'], 12),
            ('📊', 'Data Analysis with Python',      'Pandas, NumPy, Matplotlib and statistical analysis.', ['Python','Pandas','Matplotlib'], 15),
            ('🌐', 'Web Development',                'HTML, CSS, JavaScript, React, Node.js, REST APIs.', ['React','Node.js','REST'], 20),
            ('🗄️', 'Database Management',            'SQL, normalization, MySQL, PostgreSQL.', ['SQL','MySQL','NoSQL'], 10),
            ('📡', 'Computer Networking',            'OSI model, TCP/IP, subnetting, Cisco Packet Tracer.', ['TCP/IP','Cisco','Routing'], 14),
            ('☁️', 'Cloud Computing',                'AWS, Azure, Docker and Kubernetes fundamentals.', ['AWS','Docker','Cloud'], 8),
            ('🤖', 'Introduction to AI & ML',        'Machine learning basics, scikit-learn, neural networks.', ['Python','scikit-learn','ML'], 10),
            ('📱', 'Mobile App Development',         'Android development with Java/Kotlin.', ['Android','Java','Kotlin'], 12),
        ]
        for i, (icon, title, desc, tags, lessons) in enumerate(modules_data):
            Module.objects.get_or_create(
                title=title,
                defaults={
                    'description': desc, 'icon': icon, 'tags': tags,
                    'total_lessons': lessons, 'order': i,
                    'created_by': lecturers[0],
                }
            )
        self.stdout.write('  ✓ Modules created')

        # ── Online Classes ─────────────────────────────────
        from courses.models import OnlineClass
        classes_data = [
            ('Data Structures & Algorithms', 'Programming',   lecturers[0], 'Mon & Wed 09:00–11:00', 'live',     'Today: Linked Lists implementation in Python'),
            ('Network Security Fundamentals','Cybersecurity',  lecturers[1], 'Tue & Thu 14:00–16:00', 'upcoming', 'Next: Symmetric vs Asymmetric Encryption'),
            ('Database Management Systems',  'Database',       lecturers[2], 'Mon & Fri 11:00–13:00', 'upcoming', 'Next: Query Optimization & Indexing'),
            ('Web Development (React)',      'Web Dev',        lecturers[3], 'Wed & Fri 14:00–16:00', 'completed','Completed: Component lifecycle & hooks'),
        ]
        for name, subj, teacher, sched, status, desc in classes_data:
            OnlineClass.objects.get_or_create(
                name=name,
                defaults={
                    'subject': subj, 'teacher': teacher, 'schedule': sched,
                    'status': status, 'description': desc,
                    'meeting_link': f'https://meet.google.com/kiti-{subj.lower().replace(" ","-")[:10]}',
                }
            )
        self.stdout.write('  ✓ Online classes created')

        # ── Announcements ─────────────────────────────────
        from courses.models import Announcement
        anncts = [
            ('KNEC Exams Timetable Released', 'The November 2025 KNEC examinations timetable has been released.', 'exam', True),
            ('Python Module 3 Now Available', 'Module 3: Data Structures & Algorithms has been uploaded.', 'course', False),
            ('System Maintenance – Sunday',   'The portal will be offline for maintenance on Sunday.', 'admin', False),
        ]
        for title, body, atype, pinned in anncts:
            Announcement.objects.get_or_create(
                title=title,
                defaults={'body': body, 'type': atype, 'is_pinned': pinned, 'author': lecturers[0]}
            )
        self.stdout.write('  ✓ Announcements created')

        # ── Revision Papers ───────────────────────────────
        from courses.models import RevisionPaper
        papers = [
            ('KNEC Diploma ICT – Nov 2023 Paper 1', 'ICT Theory',    2023, 'Paper 1', 'knec'),
            ('KNEC Diploma ICT – Nov 2023 Paper 2', 'Practical ICT', 2023, 'Paper 2', 'knec'),
            ('KNEC Diploma ICT – July 2023',        'ICT Theory',    2023, 'Paper 1', 'knec'),
            ('KNEC Diploma ICT – Nov 2022',         'ICT Theory',    2022, 'Paper 1', 'knec'),
            ('Data Analysis – Past Questions',      'Data Analysis', 2024, 'Notes',   'notes'),
            ('Cybersecurity Revision Notes',        'Cybersecurity', 2024, 'Notes',   'notes'),
            ('Database Normalization Exercises',    'Database',      2024, 'Exercises','practice'),
            ('Networking – OSI Model Summary',      'Networking',    2024, 'Notes',   'notes'),
        ]
        for title, subj, year, paper, ptype in papers:
            RevisionPaper.objects.get_or_create(
                title=title,
                defaults={'subject': subj, 'year': year, 'paper': paper,
                          'type': ptype, 'uploaded_by': lecturers[0]}
            )
        self.stdout.write('  ✓ Revision papers created')

        # ── Assignments ───────────────────────────────────
        from assignments.models import Assignment, Submission
        assignments_data = [
            ('Network Topology Design',       'Networking',  50,  14),
            ('Python OOP – Bank System',      'Programming', 100, 9),
            ('Database Normalization Report', 'Database',    40,  12),
            ('Cybersecurity Risk Assessment', 'Cybersecurity',60, 19),
        ]
        asgns = []
        for title, subj, marks, days_from_now in assignments_data:
            asgn, _ = Assignment.objects.get_or_create(
                title=title,
                defaults={
                    'subject': subj, 'max_marks': marks,
                    'due_date': date.today() + timedelta(days=days_from_now),
                    'description': f'Complete and submit before due date. {title}.',
                    'created_by': lecturers[0],
                }
            )
            asgns.append(asgn)

        # Seed some grades
        score_map = {
            students[0]: [45, 85, 38, None],
            students[1]: [32, None, None, None],
            students[2]: [48, 90, 35, 52],
            students[4]: [50, 95, 39, 55],
        }
        for student, scores in score_map.items():
            for asgn, score in zip(asgns, scores):
                if score is not None:
                    Submission.objects.get_or_create(
                        assignment=asgn, student=student,
                        defaults={
                            'marks_obtained': score, 'submitted': True,
                            'submitted_at': timezone.now(),
                            'feedback': 'Good work!' if score >= asgn.max_marks * 0.7 else 'Needs improvement.',
                            'graded_by': lecturers[0], 'graded_at': timezone.now(),
                        }
                    )
        self.stdout.write('  ✓ Assignments & grades created')

        # ── Attendance ────────────────────────────────────
        from attendance.models import AttendanceRecord
        statuses = [
            AttendanceRecord.PRESENT, AttendanceRecord.PRESENT,
            AttendanceRecord.PRESENT, AttendanceRecord.LATE,
            AttendanceRecord.ABSENT,
        ]
        for student in students:
            for days_ago in range(14):
                d = date.today() - timedelta(days=days_ago)
                if d.weekday() >= 5:   # skip weekends
                    continue
                att_status = random.choice(statuses)
                AttendanceRecord.objects.get_or_create(
                    student=student, date=d,
                    defaults={'status': att_status, 'marked_by': lecturers[0]}
                )
        self.stdout.write('  ✓ Attendance records created')

        # ── CATs ──────────────────────────────────────────
        from assessments.models import CAT, Question
        cat1, _ = CAT.objects.get_or_create(
            title='Programming Fundamentals CAT',
            defaults={
                'subject': 'Programming', 'duration_mins': 30,
                'scheduled_date': date.today() + timedelta(days=5),
                'status': 'upcoming', 'created_by': lecturers[0],
                'instructions': 'Answer all questions. No books allowed.',
            }
        )
        questions = [
            ('What does OOP stand for?', 'Object Oriented Programming','Open Object Protocol','Optional Operating Process','Object Online Platform', 'A'),
            ('Which keyword defines a class in Python?', 'def','function','class','object', 'C'),
            ('What is the output of: print(type([]))?', "<class 'list'>",'<list>','Array','None', 'A'),
            ('Which is a mutable data type in Python?', 'String','Tuple','Integer','List', 'D'),
            ('What does __init__ do?', 'Initializes the module','Defines constructor','Imports libraries','Deletes the object', 'B'),
        ]
        for i, (text, a, b, c, d, ans) in enumerate(questions):
            Question.objects.get_or_create(
                cat=cat1, text=text,
                defaults={'option_a':a,'option_b':b,'option_c':c,'option_d':d,'correct_ans':ans,'order':i+1}
            )

        cat2, _ = CAT.objects.get_or_create(
            title='Networking Concepts CAT',
            defaults={
                'subject': 'Networking', 'duration_mins': 25,
                'scheduled_date': date.today() + timedelta(days=10),
                'status': 'upcoming', 'created_by': lecturers[1],
            }
        )
        net_qs = [
            ('How many layers does the OSI model have?', '5','6','7','8','C'),
            ('Which protocol assigns IP addresses automatically?', 'DNS','FTP','DHCP','HTTP','C'),
            ('What is the max cable length for Cat5e Ethernet?', '50m','100m','200m','500m','B'),
            ('Which OSI layer handles routing?', 'Data Link','Transport','Network','Session','C'),
        ]
        for i, (text, a, b, c, d, ans) in enumerate(net_qs):
            Question.objects.get_or_create(
                cat=cat2, text=text,
                defaults={'option_a':a,'option_b':b,'option_c':c,'option_d':d,'correct_ans':ans,'order':i+1}
            )
        self.stdout.write('  ✓ CATs created')

        # ── Collaboration Rooms ───────────────────────────
        from collaboration.models import Room, Message
        rooms_data = [
            ('ICT Year 2 General',          'class',     '💬'),
            ('Cybersecurity Study Group',   'study',     '🔐'),
            ('Python Coders',               'codespace', '🐍'),
            ('Data Analysis Team',          'study',     '📊'),
        ]
        for rname, rtype, icon in rooms_data:
            room, _ = Room.objects.get_or_create(
                name=rname,
                defaults={'type': rtype, 'icon': icon, 'created_by': lecturers[0]}
            )
            for s in students[:4]:
                room.members.add(s)
            room.members.add(lecturers[0])

        # Seed a few messages in the general room
        general = Room.objects.get(name='ICT Year 2 General')
        seed_msgs = [
            (students[0], 'Hey team! Has everyone seen the new Python module?'),
            (students[1], 'Just checked it — looks intense 😅'),
            (students[4], 'Starting it tonight after the CA 🔥'),
        ]
        for sender, text in seed_msgs:
            Message.objects.get_or_create(
                room=general, sender=sender, text=text
            )
        self.stdout.write('  ✓ Collaboration rooms & messages created')

        # ── Lecturer Notes ────────────────────────────────
        from assignments.models import LecturerNote
        notes_data = [
            (students[3], lecturers[0], 'warning',      'David — please see me after class. Your progress has been slow. Extra tutoring on Saturdays.'),
            (students[0], lecturers[0], 'commendation', 'Alice — excellent performance in all assignments. Apply for the ICT Excellence Award 2025.'),
            (students[1], lecturers[1], 'warning',      'Brian — your attendance has dropped below 80%. This is affecting your coursework grade.'),
        ]
        for student, author, ntype, content in notes_data:
            LecturerNote.objects.get_or_create(
                student=student, author=author, content=content,
                defaults={'type': ntype}
            )
        self.stdout.write('  ✓ Lecturer notes created')

        self.stdout.write(self.style.SUCCESS('\n✅  Seeding complete!\n'))
        self.stdout.write('  Login credentials:')
        self.stdout.write('  🔧 Admin:    admin@kiti.ac.ke      / admin1234')
        self.stdout.write('  👨‍🏫 Lecturer: omondi@kiti.ac.ke     / lecturer1234')
        self.stdout.write('  🎓 Student:  alice@kiti.ac.ke      / student1234')
        self.stdout.write('  🎓 Student:  brian@kiti.ac.ke      / student1234\n')
