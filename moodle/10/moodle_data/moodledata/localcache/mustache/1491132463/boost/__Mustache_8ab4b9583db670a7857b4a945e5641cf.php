<?php

class __Mustache_8ab4b9583db670a7857b4a945e5641cf extends Mustache_Template
{
    public function renderInternal(Mustache_Context $context, $indent = '')
    {
        $buffer = '';
        $blocksContext = array();

        $buffer .= $indent . '<div class="hover-tooltip-container">
';
        $buffer .= $indent . '    ';
        $blockFunction = $context->findInBlock('anchor');
        if (is_callable($blockFunction)) {
            $buffer .= call_user_func($blockFunction, $context);
        } else {
        }
        $buffer .= '
';
        $buffer .= $indent . '    <div class="hover-tooltip">
';
        $buffer .= $indent . '        ';
        $blockFunction = $context->findInBlock('tooltip');
        if (is_callable($blockFunction)) {
            $buffer .= call_user_func($blockFunction, $context);
        } else {
        }
        $buffer .= '
';
        $buffer .= $indent . '    </div>
';
        $buffer .= $indent . '</div>
';

        return $buffer;
    }
}
