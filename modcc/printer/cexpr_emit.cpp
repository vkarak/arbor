#include <cmath>
#include <iomanip>
#include <ostream>
#include <unordered_map>

#include "cexpr_emit.hpp"
#include "error.hpp"
#include "lexer.hpp"
#include "io/ostream_wrappers.hpp"
#include "io/prefixbuf.hpp"

std::ostream& operator<<(std::ostream& out, as_c_double wrap) {
    bool neg = std::signbit(wrap.value);

    switch (std::fpclassify(wrap.value)) {
    case FP_INFINITE:
        return out << (neg? "-": "") << "INFINITY";
    case FP_NAN:
        return out << "NAN";
    case FP_ZERO:
        return out << (neg? "-0.": "0.");
    default:
        return out <<
            (std::stringstream{} << io::classic << std::setprecision(17) << wrap.value).rdbuf();
    }
}

void CExprEmitter::emit_as_call(const char* sub, Expression* e) {
    out_ << sub << '(';
    e->accept(this);
    out_ << ')';
}

void CExprEmitter::emit_as_call(const char* sub, Expression* e1, Expression* e2) {
    out_ << sub << '(';
    e1->accept(this);
    out_ << ", ";
    e2->accept(this);
    out_ << ')';
}

void CExprEmitter::visit(NumberExpression* e) {
    out_ << " " << as_c_double(e->value());
}

void CExprEmitter::visit(UnaryExpression* e) {
    // Place a space in front of minus sign to avoid invalid
    // expressions of the form: (v[i]--67)
    static std::unordered_map<tok, const char*> unaryop_tbl = {
        {tok::minus,   " -"},
        {tok::exp,     "exp"},
        {tok::cos,     "cos"},
        {tok::sin,     "sin"},
        {tok::log,     "log"},
        {tok::abs,     "fabs"},
        {tok::exprelr, "exprelr"}
    };

    if (!unaryop_tbl.count(e->op())) {
        throw compiler_exception(
            "CExprEmitter: unsupported unary operator "+token_string(e->op()), e->location());
    }

    const char* op_spelling = unaryop_tbl.at(e->op());
    Expression* inner = e->expression();

    // No need to use parenthesis for unary minus if inner expression is
    // not binary.
    if (e->op()==tok::minus && !inner->is_binary()) {
        out_ << op_spelling;
        inner->accept(this);
    }
    else {
        emit_as_call(op_spelling, inner);
    }
}

void CExprEmitter::visit(AssignmentExpression* e) {
    e->lhs()->accept(this);
    out_ << " = ";
    e->rhs()->accept(this);
}

void CExprEmitter::visit(PowBinaryExpression* e) {
    emit_as_call("pow", e->lhs(), e->rhs());
}

void CExprEmitter::visit(BinaryExpression* e) {
    static std::unordered_map<tok, const char*> binop_tbl = {
        {tok::minus,    "-"},
        {tok::plus,     "+"},
        {tok::times,    "*"},
        {tok::divide,   "/"},
        {tok::lt,       "<"},
        {tok::lte,      "<="},
        {tok::gt,       ">"},
        {tok::gte,      ">="},
        {tok::equality, "=="},
        {tok::min,      "min"},
        {tok::max,      "max"},
    };

    if (!binop_tbl.count(e->op())) {
        throw compiler_exception(
            "CExprEmitter: unsupported binary operator "+token_string(e->op()), e->location());
    }

    auto rhs = e->rhs();
    auto lhs = e->lhs();
    const char* op_spelling = binop_tbl.at(e->op());

    if (e->is_infix()) {
        associativityKind assoc = Lexer::operator_associativity(e->op());
        int op_prec = Lexer::binop_precedence(e->op());

        auto need_paren = [op_prec](Expression* subexpr, bool assoc_side) -> bool {
            if (auto b = subexpr->is_binary()) {
                int sub_prec = Lexer::binop_precedence(b->op());
                return sub_prec<op_prec || (!assoc_side && sub_prec==op_prec);
            }
            return false;
        };

        if (need_paren(lhs, assoc==associativityKind::left)) {
            emit_as_call("", lhs);
        }
        else {
            lhs->accept(this);
        }

        out_ << op_spelling;

        if (need_paren(rhs, assoc==associativityKind::right)) {
            emit_as_call("", rhs);
        }
        else {
            rhs->accept(this);
        }
    }
    else {
        emit_as_call(op_spelling, lhs, rhs);
    }
}

void CExprEmitter::visit(IfExpression* e) {
    out_ << "if (";
    e->condition()->accept(this);
    out_ << ") {\n" << io::indent;
    e->true_branch()->accept(this);
    out_ << io::popindent << "}\n";

    if (auto fb = e->false_branch()) {
        out_ << "else ";
        if (fb->is_if()) {
            fb->accept(this);
        }
        else {
            out_ << "{\n" << io::indent;
            fb->accept(this);
            out_ << io::popindent << "}\n";
        }
    }
}
